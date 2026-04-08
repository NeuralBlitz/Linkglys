{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.venv
    pkgs.python311Packages.fastapi
    pkgs.python311Packages.uvicorn
    pkgs.python311Packages.pydantic
    pkgs.python311Packages.pyjwt
    pkgs.python311Packages.python-multipart
    pkgs.python311Packages.cryptography
    pkgs.python311Packages.aiofiles
    pkgs.nodejs_20
    pkgs.bun
    pkgs.git
  ];

  env = {
    PYTHONPATH = "/home/runner/workspace:${pkgs.python311Packages.pip}/lib/python3.11/site-packages";
  };
}
