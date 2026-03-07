// ================================
// Architecture Page JavaScript
// ================================

document.addEventListener('DOMContentLoaded', function() {
    initArchitectureDiagrams();
    initComponentHighlights();
    initDataFlowAnimation();
});

// ================================
// Interactive Layer Accordions
// ================================

function initArchitectureDiagrams() {
    const layerCards = document.querySelectorAll('.layer-card');
    
    layerCards.forEach((card, index) => {
        const header = card.querySelector('.layer-header');
        const content = card.querySelector('.layer-content');
        
        // Open first layer by default
        if (index === 0) {
            card.classList.add('active');
            content.style.maxHeight = content.scrollHeight + 'px';
        }
        
        header.addEventListener('click', function() {
            const isActive = card.classList.contains('active');
            
            // Close all layers
            layerCards.forEach(c => {
                c.classList.remove('active');
                const cont = c.querySelector('.layer-content');
                cont.style.maxHeight = '0';
            });
            
            // Open clicked layer if it wasn't active
            if (!isActive) {
                card.classList.add('active');
                content.style.maxHeight = content.scrollHeight + 'px';
                
                // Scroll layer into view
                setTimeout(() => {
                    card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 300);
            }
        });
    });
}

// ================================
// Component Highlights
// ================================

function initComponentHighlights() {
    const componentBoxes = document.querySelectorAll('.component-box');
    
    componentBoxes.forEach(box => {
        box.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.02)';
            this.style.boxShadow = '0 10px 30px rgba(14, 165, 233, 0.3)';
        });
        
        box.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
            this.style.boxShadow = '';
        });
    });
}

// ================================
// Data Flow Animation
// ================================

function initDataFlowAnimation() {
    const flowSteps = document.querySelectorAll('.flow-step');
    
    // Observe when flow diagram comes into view
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateFlowSteps(flowSteps);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    const flowDiagram = document.querySelector('.flow-diagram');
    if (flowDiagram) {
        observer.observe(flowDiagram);
    }
}

function animateFlowSteps(steps) {
    steps.forEach((step, index) => {
        step.style.opacity = '0';
        step.style.transform = 'translateX(-30px)';
        
        setTimeout(() => {
            step.style.transition = 'all 0.5s ease';
            step.style.opacity = '1';
            step.style.transform = 'translateX(0)';
        }, index * 200);
    });
}

// ================================
// AGI Component Interactions
// ================================

function initAGIComponents() {
    const agiComponents = document.querySelectorAll('.agi-component');
    
    agiComponents.forEach(component => {
        component.addEventListener('click', function() {
            const componentName = this.querySelector('h3').textContent;
            showAGIDetails(componentName);
        });
    });
}

function showAGIDetails(name) {
    // Could expand to show modal with detailed implementation info
    console.log(`AGI Component: ${name}`);
    window.jarvisUtils.showNotification(`Learn more about ${name} in the Code Library`, 'info');
}

document.addEventListener('DOMContentLoaded', initAGIComponents);

// ================================
// Deployment Architecture Toggle
// ================================

function initDeploymentToggle() {
    const deploymentCards = document.querySelectorAll('.deployment-card');
    
    deploymentCards.forEach(card => {
        card.addEventListener('click', function() {
            deploymentCards.forEach(c => c.classList.remove('selected'));
            this.classList.add('selected');
            
            const deploymentType = this.querySelector('h3').textContent;
            saveDeploymentPreference(deploymentType);
        });
    });
    
    // Load saved preference
    const savedDeployment = localStorage.getItem('jarvis-deployment');
    if (savedDeployment) {
        deploymentCards.forEach(card => {
            if (card.querySelector('h3').textContent.includes(savedDeployment)) {
                card.classList.add('selected');
            }
        });
    }
}

function saveDeploymentPreference(type) {
    const simplified = type.toLowerCase().includes('local') ? 'local' : 'cloud';
    localStorage.setItem('jarvis-deployment', simplified);
    window.jarvisUtils.showNotification(`Deployment preference saved: ${simplified}`, 'success');
}

document.addEventListener('DOMContentLoaded', initDeploymentToggle);

// ================================
// Tool Showcase Interaction
// ================================

function initToolShowcase() {
    const toolItems = document.querySelectorAll('.tool-item');
    
    toolItems.forEach(item => {
        item.addEventListener('click', function() {
            const toolName = this.textContent.trim();
            showToolInfo(toolName);
        });
    });
}

function showToolInfo(toolName) {
    // Navigate to code library with filter
    window.location.href = `code-library.html?filter=${encodeURIComponent(toolName)}`;
}

document.addEventListener('DOMContentLoaded', initToolShowcase);

// ================================
// Layer Navigation
// ================================

function createLayerNavigation() {
    const layerCards = document.querySelectorAll('.layer-card');
    if (layerCards.length === 0) return;
    
    const nav = document.createElement('div');
    nav.className = 'layer-navigation';
    nav.innerHTML = '<h4>Quick Navigate:</h4>';
    
    const navList = document.createElement('div');
    navList.className = 'layer-nav-list';
    
    layerCards.forEach((card, index) => {
        const layerTitle = card.querySelector('h3').textContent;
        const layerNum = card.getAttribute('data-layer');
        
        const navItem = document.createElement('button');
        navItem.className = 'layer-nav-item';
        navItem.textContent = `${layerNum}. ${layerTitle}`;
        navItem.addEventListener('click', () => {
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.querySelector('.layer-header').click();
        });
        
        navList.appendChild(navItem);
    });
    
    nav.appendChild(navList);
    
    // Insert before first layer
    const layersContainer = layerCards[0].parentElement;
    layersContainer.insertBefore(nav, layerCards[0]);
}

document.addEventListener('DOMContentLoaded', createLayerNavigation);

// ================================
// Diagram Zoom
// ================================

function initDiagramZoom() {
    const diagrams = document.querySelectorAll('.architecture-diagram, .system-diagram, .network-diagram pre');
    
    diagrams.forEach(diagram => {
        diagram.style.cursor = 'zoom-in';
        
        diagram.addEventListener('click', function() {
            if (this.classList.contains('zoomed')) {
                this.classList.remove('zoomed');
                this.style.cursor = 'zoom-in';
            } else {
                this.classList.add('zoomed');
                this.style.cursor = 'zoom-out';
            }
        });
    });
}

document.addEventListener('DOMContentLoaded', initDiagramZoom);

// ================================
// Copy Network Diagram
// ================================

function addCopyButtonToDiagrams() {
    const networkDiagrams = document.querySelectorAll('.network-diagram');
    
    networkDiagrams.forEach(diagramContainer => {
        const pre = diagramContainer.querySelector('pre');
        if (!pre) return;
        
        const copyBtn = document.createElement('button');
        copyBtn.className = 'diagram-copy-btn';
        copyBtn.innerHTML = '<i class="fas fa-copy"></i> Copy Diagram';
        copyBtn.addEventListener('click', () => {
            window.jarvisUtils.copyToClipboard(pre.textContent);
        });
        
        diagramContainer.insertBefore(copyBtn, pre);
    });
}

document.addEventListener('DOMContentLoaded', addCopyButtonToDiagrams);