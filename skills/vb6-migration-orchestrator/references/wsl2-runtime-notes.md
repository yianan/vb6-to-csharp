# WSL2 Runtime Notes

Use this for migrated VB6-to-.NET/React apps that must run fully inside WSL2.

## Runtime Constraints

- ASP.NET Core runs well in WSL2.
- React/Vite runs well in WSL2.
- EF Core with SQLite or PostgreSQL runs well in WSL2.
- WinForms, WPF, VB6 runtimes, OCX controls, COM registration, Access OLEDB, and Windows registry dependencies are Windows concerns.

## Environment Checks

```bash
dotnet --info
node --version
npm --version
```

If system `dotnet` is broken or mixed across package sources, install or use a local SDK and call it by absolute path:

```bash
./.dotnet/dotnet --info
./.dotnet/dotnet build
```

If system Node is missing `npm`, too old, or reports engine warnings, use a local Node runtime and prefix commands:

```bash
PATH="$PWD/.node/bin:$PATH" npm --version
PATH="$PWD/.node/bin:$PATH" npm install
PATH="$PWD/.node/bin:$PATH" npm run build
```

Package installs under `/mnt/c` can be slow. Prefer a native Linux filesystem for large frontend dependency trees when possible.

## Run Commands

Backend:

```bash
dotnet restore
dotnet build
dotnet test
dotnet run --project backend/<App>.Api --urls http://localhost:5174
```

Frontend:

```bash
npm --prefix frontend install
npm --prefix frontend run lint
npm --prefix frontend run build
npm --prefix frontend run dev -- --host 127.0.0.1 --port 5173
```

Restart backend processes after endpoint/service changes before smoke testing. Frontend dev servers may hot reload, but stale Vite sessions can still mask route/shell changes.

## Live Smoke Checklist

After starting backend and frontend:

1. Open the unauthenticated app and verify the startup screen matches the VB6 startup flow.
2. Submit a public record if the source had public submission.
3. Log in with seed credentials.
4. List, search, page, create, edit, delete, and mutate each migrated entity.
5. Confirm money, balance, quantity, or total workflows cap/reject/update values like the source.
6. Confirm role-gated actions are visible, hidden, and server-protected as in the source.
7. Confirm sensitive actions require password confirmation when the VB6 app required it.
8. Hard-refresh after restarts and verify the served source contains the latest changed strings/classes when in doubt.
