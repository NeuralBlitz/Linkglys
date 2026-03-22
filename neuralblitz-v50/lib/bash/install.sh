#!/bin/bash
# NeuralBlitz v50.0 - CLI Installer
# Installs NeuralBlitz and all dependencies

set -e

VERSION="50.0.0"
INSTALL_DIR="${HOME}/.neuralblitz"
PYTHON_MIN_VERSION="3.8"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 not found. Please install Python 3.8+"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    log_info "Found Python ${PYTHON_VERSION}"
}

check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check required Python packages
    python3 -c "import numpy" 2>/dev/null || {
        log_warn "numpy not found, installing..."
        pip3 install numpy
    }
    
    python3 -c "import hashlib" 2>/dev/null || {
        log_error "hashlib not found"
        exit 1
    }
    
    log_info "All dependencies satisfied"
}

install_neuralblitz() {
    log_info "Installing NeuralBlitz v${VERSION}..."
    
    # Create install directory
    mkdir -p "${INSTALL_DIR}"
    
    # Copy Python package
    if [ -d "neuralblitz-v50/python" ]; then
        cp -r neuralblitz-v50/python/* "${INSTALL_DIR}/"
        log_info "Copied Python package"
    fi
    
    # Create entry point
    cat > "${INSTALL_DIR}/nb" << 'EOF'
#!/bin/bash
INSTALL_DIR="${HOME}/.neuralblitz"
python3 -m neuralblitz.cli "$@"
EOF
    chmod +x "${INSTALL_DIR}/nb"
    
    # Add to PATH
    SHELL_RC="${HOME}/.bashrc"
    if [ -f "${HOME}/.zshrc" ]; then
        SHELL_RC="${HOME}/.zshrc"
    fi
    
    if ! grep -q "neuralblitz" "${SHELL_RC}"; then
        echo "export PATH=\"\${PATH}:${INSTALL_DIR}\"" >> "${SHELL_RC}"
    fi
    
    log_info "NeuralBlitz installed successfully!"
}

main() {
    log_info "NeuralBlitz v${VERSION} Installer"
    echo "=================================="
    
    check_python
    check_dependencies
    install_neuralblitz
    
    log_info "Installation complete!"
    log_info "Run 'nb info' to verify installation"
}

main "$@"
