# 🚀 AGI Research Starter Kit
## Ready-to-use templates for each path

Pick your path, clone the template, start implementing.

---

## 📁 Repository Structure

```
agi_research/
├── path1_world_models/
├── path2_continual_learning/
├── path3_reasoning/
├── path4_grounded_language/
├── path5_meta_learning/
└── README.md  ← You are here
```

---

## 🎯 Quick Start (All Paths)

```bash
# Create environment
conda create -n agi python=3.10
conda activate agi

# Install base dependencies
pip install torch torchvision numpy matplotlib wandb
pip install gym stable-baselines3 tensorboard

# Choose your path and cd into it
cd path1_world_models/  # or path2, path3, etc.

# Run baseline
python reproduce_baseline.py

# Implement your idea
python your_method.py

# Evaluate
python evaluate.py
```

---

## PATH 1: World Models 🌍

### Starter Code: `world_model_template.py`

```python
import torch
import torch.nn as nn
import torch.nn.functional as F
import gym

class WorldModel(nn.Module):
    """
    Learn a model of environment dynamics.
    Predict next state from current state + action.
    """
    def __init__(self, state_dim, action_dim, latent_dim=32):
        super().__init__()
        
        # Encoder: observation -> latent state
        self.encoder = nn.Sequential(
            nn.Linear(state_dim, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim * 2)  # mean + logvar
        )
        
        # Transition model: (latent, action) -> next latent
        self.transition = nn.Sequential(
            nn.Linear(latent_dim + action_dim, 128),
            nn.ReLU(),
            nn.Linear(128, latent_dim)
        )
        
        # Decoder: latent -> observation
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Linear(128, state_dim)
        )
        
        # Reward predictor
        self.reward_pred = nn.Linear(latent_dim, 1)
    
    def encode(self, obs):
        """Encode observation to latent"""
        h = self.encoder(obs)
        mean, logvar = torch.chunk(h, 2, dim=-1)
        std = torch.exp(0.5 * logvar)
        z = mean + std * torch.randn_like(std)
        return z, mean, logvar
    
    def predict_next(self, z, action):
        """Predict next latent state"""
        za = torch.cat([z, action], dim=-1)
        z_next = self.transition(za)
        return z_next
    
    def decode(self, z):
        """Decode latent to observation"""
        obs_pred = self.decoder(z)
        return obs_pred
    
    def forward(self, obs, action):
        """Full forward pass"""
        z, mean, logvar = self.encode(obs)
        z_next = self.predict_next(z, action)
        obs_next_pred = self.decode(z_next)
        reward_pred = self.reward_pred(z_next)
        return obs_next_pred, reward_pred, mean, logvar


def train_world_model():
    """Training loop"""
    env = gym.make('CartPole-v1')
    model = WorldModel(state_dim=4, action_dim=2)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Collect data
    buffer = []
    for episode in range(100):
        obs = env.reset()
        done = False
        while not done:
            action = env.action_space.sample()
            obs_next, reward, done, _ = env.step(action)
            buffer.append((obs, action, obs_next, reward))
            obs = obs_next
    
    # Train
    for epoch in range(1000):
        # Sample batch
        batch = random.sample(buffer, 64)
        obs, actions, obs_next, rewards = zip(*batch)
        
        obs = torch.FloatTensor(obs)
        actions = torch.LongTensor(actions)
        obs_next = torch.FloatTensor(obs_next)
        rewards = torch.FloatTensor(rewards)
        
        # Forward
        obs_next_pred, reward_pred, mean, logvar = model(obs, actions)
        
        # Losses
        recon_loss = F.mse_loss(obs_next_pred, obs_next)
        reward_loss = F.mse_loss(reward_pred.squeeze(), rewards)
        kl_loss = -0.5 * torch.sum(1 + logvar - mean.pow(2) - logvar.exp())
        
        loss = recon_loss + reward_loss + 0.001 * kl_loss
        
        # Backward
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if epoch % 100 == 0:
            print(f"Epoch {epoch}, Loss: {loss.item():.4f}")
    
    return model


if __name__ == "__main__":
    model = train_world_model()
    torch.save(model.state_dict(), 'world_model.pt')
```

### Next Steps for Path 1:
1. Run this baseline
2. Add physics priors (YOUR CONTRIBUTION)
3. Test on harder environments (MuJoCo)
4. Write paper

---

## PATH 2: Continual Learning 🔄

### Starter Code: `continual_learning_template.py`

```python
import torch
import torch.nn as nn
import torchvision
import copy

class ContinualLearner(nn.Module):
    """
    Learn multiple tasks sequentially without forgetting.
    """
    def __init__(self, input_dim=784, hidden_dim=256, num_classes=10):
        super().__init__()
        self.features = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden_dim, num_classes)
        
        # For EWC: store Fisher information
        self.fisher = {}
        self.old_params = {}
    
    def forward(self, x):
        h = self.features(x.view(x.size(0), -1))
        out = self.classifier(h)
        return out
    
    def compute_fisher(self, dataloader):
        """Compute Fisher Information Matrix"""
        fisher = {n: torch.zeros_like(p) for n, p in self.named_parameters()}
        
        self.eval()
        for x, y in dataloader:
            self.zero_grad()
            output = self(x)
            loss = F.cross_entropy(output, y)
            loss.backward()
            
            for n, p in self.named_parameters():
                if p.grad is not None:
                    fisher[n] += p.grad.data ** 2
        
        # Normalize
        n_samples = len(dataloader.dataset)
        fisher = {n: f / n_samples for n, f in fisher.items()}
        return fisher
    
    def ewc_loss(self, lambda_ewc=1000):
        """Elastic Weight Consolidation loss"""
        loss = 0
        for n, p in self.named_parameters():
            if n in self.fisher:
                loss += (self.fisher[n] * (p - self.old_params[n]) ** 2).sum()
        return lambda_ewc * loss
    
    def save_task(self, dataloader):
        """After learning task, save Fisher and parameters"""
        self.fisher = self.compute_fisher(dataloader)
        self.old_params = {n: p.clone().detach() for n, p in self.named_parameters()}


def train_continual():
    """Train on multiple tasks"""
    # Task 1: MNIST
    train_loader_1 = torch.utils.data.DataLoader(
        torchvision.datasets.MNIST('./data', train=True, download=True,
                                   transform=torchvision.transforms.ToTensor()),
        batch_size=64, shuffle=True
    )
    
    # Task 2: FashionMNIST
    train_loader_2 = torch.utils.data.DataLoader(
        torchvision.datasets.FashionMNIST('./data', train=True, download=True,
                                          transform=torchvision.transforms.ToTensor()),
        batch_size=64, shuffle=True
    )
    
    model = ContinualLearner()
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Train Task 1
    print("Training Task 1 (MNIST)...")
    for epoch in range(5):
        for x, y in train_loader_1:
            optimizer.zero_grad()
            output = model(x)
            loss = F.cross_entropy(output, y)
            loss.backward()
            optimizer.step()
    
    # Evaluate on Task 1
    acc_1_before = evaluate(model, train_loader_1)
    print(f"Task 1 accuracy before Task 2: {acc_1_before:.2%}")
    
    # Save Fisher info
    model.save_task(train_loader_1)
    
    # Train Task 2 (with EWC)
    print("Training Task 2 (FashionMNIST)...")
    for epoch in range(5):
        for x, y in train_loader_2:
            optimizer.zero_grad()
            output = model(x)
            loss = F.cross_entropy(output, y) + model.ewc_loss()
            loss.backward()
            optimizer.step()
    
    # Evaluate on both tasks
    acc_1_after = evaluate(model, train_loader_1)
    acc_2 = evaluate(model, train_loader_2)
    
    print(f"Task 1 accuracy after Task 2: {acc_1_after:.2%}")
    print(f"Task 2 accuracy: {acc_2:.2%}")
    print(f"Forgetting: {(acc_1_before - acc_1_after):.2%}")


def evaluate(model, dataloader):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in dataloader:
            output = model(x)
            pred = output.argmax(dim=1)
            correct += (pred == y).sum().item()
            total += y.size(0)
    return correct / total


if __name__ == "__main__":
    train_continual()
```

### Next Steps for Path 2:
1. Run this EWC baseline
2. Implement PackNet, Progressive Nets
3. Add YOUR novel method
4. Test on Split-CIFAR100

---

## 📚 Paper Reading Lists (For Each Path)

### Path 1: World Models
**Must-read (in order)**:
1. World Models (Ha & Schmidhuber, 2018)
2. PlaNet (Hafner et al., 2019)
3. Dreamer (Hafner et al., 2020)
4. DreamerV2 (Hafner et al., 2021)
5. IRIS (Micheli et al., 2022)

### Path 2: Continual Learning
**Must-read**:
1. Overcoming Catastrophic Forgetting (Kirkpatrick et al., 2017) - EWC
2. Progressive Neural Networks (Rusu et al., 2016)
3. PackNet (Mallya & Lazebnik, 2018)
4. Experience Replay for Continual Learning (Rolnick et al., 2019)
5. Dark Experience for General Continual Learning (Buzzega et al., 2020)

### Path 3: Reasoning
**Must-read**:
1. Neural Module Networks (Andreas et al., 2016)
2. The Neuro-Symbolic Concept Learner (Mao et al., 2019)
3. Chain-of-Thought Prompting (Wei et al., 2022)
4. Abstraction and Reasoning Corpus (Chollet, 2019)
5. System 2 Attention (Weston & Sukhbaatar, 2023)

### Path 4: Grounded Language
**Must-read**:
1. CLIP (Radford et al., 2021)
2. Flamingo (Alayrac et al., 2022)
3. RT-2 (Brohan et al., 2023)
4. PaLM-E (Driess et al., 2023)
5. ALFRED (Shridhar et al., 2020)

### Path 5: Meta-Learning
**Must-read**:
1. MAML (Finn et al., 2017)
2. Reptile (Nichol et al., 2018)
3. Meta-World (Yu et al., 2020)
4. Learning to Learn by Gradient Descent (Andrychowicz et al., 2016)
5. Meta-Dataset (Triantafillou et al., 2020)

---

## 🎯 Which Path Do You Choose?

**Reply with your choice:**
1. 🌍 World Models
2. 🔄 Continual Learning
3. 🧮 Reasoning & Planning
4. 🗣️ Grounded Language
5. 🧠 Meta-Learning

**I'll provide:**
- Complete starter repository
- Full paper list (20+ papers)
- Exact hyperparameters
- Known failure modes
- Ideas for your contribution

**You have the math. Let's implement.** 🔥
