import "./globals.css";

import type { ReactNode } from "react";

export const metadata = {
  title: "Parser Portal",
  description: "Upload statements or invoices and download parsed CSVs through the Azure API gateway.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="page-shell">
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
