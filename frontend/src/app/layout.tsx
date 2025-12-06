import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ViWO Protocol - Token Economy Simulator',
  description: 'Interactive token economy simulator with Monte Carlo and Agent-Based modeling',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50 min-h-screen">
        {children}
      </body>
    </html>
  )
}



















