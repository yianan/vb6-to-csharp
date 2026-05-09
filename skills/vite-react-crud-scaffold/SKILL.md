---
name: vite-react-crud-scaffold
description: Exact recipe to scaffold a Vite + React + TypeScript frontend with TanStack Query, react-router, cookie-based auth, and reusable DataGrid + Dialog components. Auto-load when starting Phase 3 of a VB6 → modern-stack migration, or any time a fresh CRUD frontend over an authenticated REST backend is needed.
---

# Vite + React + TypeScript CRUD frontend — scaffold recipe

This is the exact recipe used to build the seed library app's frontend. Pairs with the `dotnet-sqlite-scaffold` skill on the backend.

## Prerequisites

- Node 20+. `node --version`.

## Scaffold

From the project root (which already has `backend/`):

```sh
npm create vite@latest frontend -- --template react-ts -y
cd frontend
npm install
npm install react-router-dom @tanstack/react-query zod
```

`zod` is for form validation; skip if your forms are simple enough that hand-rolled checks suffice.

## Project structure

```
frontend/
├── package.json
├── vite.config.ts            # /api proxy + port + strictPort
├── tsconfig*.json
├── index.html
├── src/
│   ├── main.tsx              # QueryClientProvider + AuthProvider + StrictMode
│   ├── App.tsx               # router with auth guard
│   ├── index.css             # global CSS variables + base styles
│   ├── api/
│   │   └── client.ts         # typed fetch wrapper + DTO interfaces
│   ├── auth/
│   │   └── AuthContext.tsx   # me/login/logout/changePassword via TanStack Query
│   ├── components/
│   │   ├── DataGrid.tsx
│   │   └── Dialog.tsx
│   └── pages/
│       ├── LoginPage.tsx
│       ├── Layout.tsx        # sidebar + Outlet
│       ├── BooksPage.tsx     # canonical CRUD page; copy for other resources
│       └── …
└── public/
```

## `vite.config.ts`

```ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5180,        // or 5173; check for conflicts (Docker often holds 5173)
    strictPort: true,  // fail if port unavailable, don't silently jump
    proxy: {
      '/api': { target: 'http://localhost:5174', changeOrigin: false },
    },
  },
})
```

The proxy makes `/api/*` same-origin from the browser's perspective — cookies just work, no CORS headaches.

## Typed fetch client

```ts
// src/api/client.ts
export class ApiError extends Error {
  status: number
  body?: unknown
  constructor(status: number, message: string, body?: unknown) {
    super(message)
    this.status = status
    this.body = body
  }
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const res = await fetch(path, {
    method,
    credentials: 'include',
    headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let parsed: unknown
    try { parsed = await res.json() } catch {}
    const msg = (parsed as { error?: string } | undefined)?.error ?? res.statusText
    throw new ApiError(res.status, msg, parsed)
  }
  if (res.status === 204) return undefined as T
  return res.json() as Promise<T>
}

export const api = {
  get:  <T>(path: string)              => request<T>('GET',    path),
  post: <T>(path: string, body?: any)  => request<T>('POST',   path, body),
  put:  <T>(path: string, body?: any)  => request<T>('PUT',    path, body),
  del:  <T>(path: string)              => request<T>('DELETE', path),
}
```

**Heads up**: Vite's `tsconfig` enables `erasableSyntaxOnly`, which forbids TypeScript parameter properties (`constructor(public x: number)`). Use explicit fields + assignment as above.

## AuthContext pattern

```tsx
// src/auth/AuthContext.tsx
export function AuthProvider({ children }: { children: ReactNode }) {
  const qc = useQueryClient()
  const { data, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      try { return await api.get<Me>('/api/auth/me') }
      catch (e) {
        if (e instanceof ApiError && e.status === 401) return null
        throw e
      }
    },
  })
  // value with login/logout/changePassword that update the cache via setQueryData
}
```

## Auth guard

```tsx
// src/App.tsx
function Protected({ children }: { children: ReactNode }) {
  const { me, loading } = useAuth()
  if (loading) return <div>Loading…</div>
  if (!me) return <Navigate to="/login" replace />
  return <>{children}</>
}

<Routes>
  <Route path="/login" element={<LoginPage />} />
  <Route element={<Protected><Layout /></Protected>}>
    <Route index element={<Navigate to="/books" replace />} />
    <Route path="/books" element={<BooksPage />} />
    {/* … */}
  </Route>
</Routes>
```

## Reusable DataGrid + Dialog

The DataGrid takes `rows`, `columns: { header, cell, width? }[]`, `rowKey`, optional `actions`. Use it for every list view — collapses 3+ separate VB6 grid forms into one component. (See the seed library app's `frontend/src/components/DataGrid.tsx` for the working version.)

The Dialog wraps a centered card with a backdrop, takes `title`/`busy`/`error`/`onSubmit`/`onCancel`/children. Use for every edit form.

## CRUD page pattern

`BooksPage.tsx` in the seed app is the canonical pattern:

1. `useState` for the search term and the editing target (a row, `'new'`, or `null`).
2. `useQuery({ queryKey: ['books', q], queryFn: () => api.get(...) })` for the list.
3. `useMutation` for save (POST or PUT depending on whether `id` is set) and delete.
4. `<DataGrid>` for the list with per-row `Edit`/`Delete` actions.
5. `<Dialog>` (rendered conditionally on `editing`) holding a form with controlled inputs.

Every other CRUD page is a copy of this with different fields. Don't over-abstract — the duplication is shallow and the pages stay readable.

## Copying for new resources

When adding a new resource page (e.g. `MembersPage`):

1. Add a typed DTO to `src/api/client.ts` (mirror the C# DTO).
2. Copy `BooksPage.tsx` to `MembersPage.tsx`.
3. Find/replace `Book` → `Member`, `book` → `member`, `books` → `members`.
4. Adjust the `columns` array and the editor's fields.
5. Add the route in `App.tsx` and the link in `Layout.tsx`.

Takes 10 minutes per resource.

## Common gotchas

- **Port 5173 conflict**: Docker Desktop and several other tools squat on it. Use 5180 (or anything 5180–5189) and set `strictPort: true` so Vite fails loud if the port is taken — silent fallback to a new port breaks the backend's CORS allowlist.
- **`credentials: 'include'`** is required for cookies to be sent on cross-origin fetches. With the Vite proxy this is technically same-origin, but include it anyway for production deployments.
- **`erasableSyntaxOnly`** in Vite's TS config forbids parameter properties and a few other constructs. If a build fails with `TS1294`, that's why.
- **Strict mode double-mount in dev**: `<StrictMode>` mounts components twice during development. If `useEffect` does something with side effects, guard with a flag or use TanStack Query (which is idempotent).

## Production build

```sh
npm run build      # outputs to dist/
npm run preview    # serve the build locally
```

For a single-binary deploy, copy `dist/` into the ASP.NET Core project and serve via `app.UseStaticFiles()` + `app.MapFallbackToFile("index.html")`. (Not done in the seed app; the dev split is fine for local-first.)
