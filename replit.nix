{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
    pkgs.bun
  ];

  # Python packages
  installPhase = ''
    pip install --upgrade pip
    pip install fastapi uvicorn pydantic PyJWT python-multipart cryptography aiofiles
  '';

  # Node packages
  nodejs = pkgs.nodejs_20;
}
