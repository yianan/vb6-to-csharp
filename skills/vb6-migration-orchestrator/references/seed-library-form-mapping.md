# Seed library form mapping

The Tonamalu library migration collapsed 14 VB6 forms into 7 React routes.

| VB6 form | Purpose | React route | API endpoints |
|---|---|---|---|
| `Login.frm` | Authenticate user | `/login` | `POST /api/auth/login` |
| `MDIlibrary.frm` | Top-level menu | sidebar in `Layout.tsx` | - |
| `Member.frm` | Add member | `/members` new-member dialog | `POST /api/members` |
| `member_details.frm` | Search/edit/delete member | `/members` edit dialog | `GET/PUT/DELETE /api/members/:id` |
| `Member_full_details2.frm` | Grid of all members | `/members` list | `GET /api/members` |
| `Book1.frm` | Register book | `/books` new-book dialog | `POST /api/books` |
| `Book_Details.frm` | Search/edit/delete book | `/books` edit dialog | `GET/PUT/DELETE /api/books/:id` |
| `entire_book_details1.frm` | Grid of all books | `/books` list | `GET /api/books` |
| `Studentbook.frm` | Issue a book | `/loans` issue dialog | `POST /api/loans` |
| `Students.frm` | Return a book and calculate fine | `/loans` return action | `POST /api/loans/:id/return`, `GET /api/fines/preview` |
| `Fine.frm` | Fine preview | return dialog | `GET /api/fines/preview?loanId=...` |
| `Fine_details.frm` | Recorded fines | `/fines` | `GET /api/fines`, `POST /api/fines/:id/pay` |
| `librarian.frm` | Manage librarians | `/librarians` | `GET/POST/PUT/DELETE /api/librarians` |
| `changepass.frm` | Change password | `/account/password` | `POST /api/auth/change-password` |

Pattern to reuse: merge add/search/detail/grid VB6 forms into one route per resource when the original split was only UI navigation ceremony.
