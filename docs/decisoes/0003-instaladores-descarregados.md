# 0003 — Instaladores descarregados dos sites oficiais, com verificação

- **Estado:** aceite (2026-10-22)
- **Contexto:** 84 MB de instaladores no git pesariam para sempre no histórico; o VC++ tem redistribuição em
  zona cinzenta.
- **Decisão:** os `.exe` não vão no repositório (`.gitignore`). O `instalar.ps1` usa os de `1-instaladores\` se
  passarem na verificação; senão descarrega-os: GlazeWM e Python com **SHA-256 fixo**, VC++ com **assinatura
  Authenticode da Microsoft** (o ficheiro muda no mesmo endereço). Um ficheiro que não passe nunca é executado.
- **Consequências:** a instalação precisa de internet (ou dos ficheiros postos à mão). Ver `docs/instalacao.md`
  §6.1.
