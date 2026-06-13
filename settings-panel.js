// ========== SISTEMA DE MODO OSCURO/CLARO ==========

let isDarkMode = false;

// Función para cargar la preferencia guardada
function loadThemePreference() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        isDarkMode = true;
        enableDarkMode();
    } else if (savedTheme === 'light') {
        isDarkMode = false;
        enableLightMode();
    } else {
        // Detectar preferencia del sistema
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        if (prefersDark) {
            isDarkMode = true;
            enableDarkMode();
            localStorage.setItem('theme', 'dark');
        } else {
            isDarkMode = false;
            enableLightMode();
            localStorage.setItem('theme', 'light');
        }
    }
}

// Activar modo oscuro
function enableDarkMode() {
    isDarkMode = true;
    document.body.classList.add('dark-mode');
    localStorage.setItem('theme', 'dark');
    updateThemeButtonIcon();
}

// Activar modo claro
function enableLightMode() {
    isDarkMode = false;
    document.body.classList.remove('dark-mode');
    localStorage.setItem('theme', 'light');
    updateThemeButtonIcon();
}

// Alternar entre modos
function toggleTheme() {
    if (isDarkMode) {
        enableLightMode();
    } else {
        enableDarkMode();
    }
}

// Actualizar icono del botón de tema
function updateThemeButtonIcon() {
    const themeToggleBtn = $('#themeToggleBtn');
    if (themeToggleBtn.length) {
        if (isDarkMode) {
            themeToggleBtn.html('<i class="fas fa-sun"></i> Modo claro');
        } else {
            themeToggleBtn.html('<i class="fas fa-moon"></i> Modo oscuro');
        }
    }
}

// ========== PANEL DE AJUSTES (SOLO MODO OSCURO/CLARO) ==========

// Crear panel flotante de ajustes
function createSettingsPanel() {
    if ($('#settingsPanel').length) return;
    
    const panelHtml = `
        <div id="settingsPanel" class="settings-panel">
            <div class="settings-panel-header">
                <h3><i class="fas fa-cog"></i> Ajustes</h3>
                <button class="settings-close-btn" id="closeSettingsPanel">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="settings-panel-body">
                <div class="settings-section">
                    <h4><i class="fas fa-palette"></i> Apariencia</h4>
                    <div class="settings-option">
                        <span>Tema</span>
                        <div class="theme-switch-container">
                            <button id="themeToggleBtn" class="theme-toggle-btn">
                                <i class="fas ${isDarkMode ? 'fa-sun' : 'fa-moon'}"></i>
                                ${isDarkMode ? 'Modo claro' : 'Modo oscuro'}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div id="settingsOverlay" class="settings-overlay"></div>
    `;
    
    $('body').append(panelHtml);
    
    $('#closeSettingsPanel, #settingsOverlay').on('click', function() {
        closeSettingsPanel();
    });
    
    $('#themeToggleBtn').on('click', function() {
        toggleTheme();
    });
}

// Abrir panel de ajustes
function openSettingsPanel() {
    createSettingsPanel();
    $('#settingsPanel').addClass('open');
    $('#settingsOverlay').addClass('show');
}

// Cerrar panel de ajustes
function closeSettingsPanel() {
    $('#settingsPanel').removeClass('open');
    $('#settingsOverlay').removeClass('show');
    setTimeout(() => {
        $('#settingsPanel, #settingsOverlay').remove();
    }, 300);
}

// Inicializar
$(document).ready(function() {
    loadThemePreference();
    
    // Evento para el botón de ajustes en la barra lateral
    $(document).on('click', '.nav-item:contains("Ajustes"), #settingsNavBtn', function() {
        openSettingsPanel();
    });
});