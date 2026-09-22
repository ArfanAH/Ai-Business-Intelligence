import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "AI Business Intelligence",
  description: "AI-powered business intelligence dashboard",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-100">
        <div className="flex min-h-screen flex-col">
          <div className="flex-1">
            {children}
          </div>

          <footer className="border-t border-gray-200 bg-white py-5 text-center">
            <p className="text-sm text-gray-800">
              © 2026
            </p>

            <p className="mt-1 text-sm font-medium text-gray-900">
              Developed by Md. Arfan Ahmed
            </p>
          </footer>
        </div>
      </body>
    </html>
  );
}