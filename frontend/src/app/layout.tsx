import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import Script from 'next/script';
import './globals.css';
import PWAInstallBanner from '@/components/pwa/PWAInstallBanner';
import OfflineIndicator from '@/components/common/OfflineIndicator';
import PWAServiceWorker from '@/components/pwa/PWAServiceWorker';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'GreenSteel - ESG Management Platform',
  description:
    'Comprehensive ESG management platform for LCA, CBAM, and sustainability reporting. Track your environmental impact and compliance.',
  keywords:
    'ESG, LCA, CBAM, sustainability, carbon footprint, green steel, PWA, progressive web app',
  authors: [{ name: 'GreenSteel Team' }],
  creator: 'GreenSteel',
  publisher: 'GreenSteel',
  robots: 'index, follow',
  openGraph: {
    title: 'GreenSteel - ESG Management Platform',
    description:
      'Comprehensive ESG management platform for LCA, CBAM, and sustainability reporting. Track your environmental impact and compliance.',
    url: 'https://greensteel.site',
    siteName: 'GreenSteel',
    locale: 'ko_KR',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'GreenSteel - ESG Management Platform',
    description:
      'Comprehensive ESG management platform for LCA, CBAM, and sustainability reporting. Track your environmental impact and compliance.',
  },
  other: {
    'csrf-token': '{{csrf_token}}',
    'mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-capable': 'yes',
    'apple-mobile-web-app-status-bar-style': 'default',
    'apple-mobile-web-app-title': 'GreenSteel',
    'msapplication-TileColor': '#3b82f6',
    'theme-color': '#3b82f6',
    'application-name': 'GreenSteel',
    'msapplication-TileImage': '/icon-192x192.svg',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
  viewportFit: 'cover',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang='ko' className='dark'>
      <head>
        <link rel='manifest' href='/manifest.json' />
        <link rel='icon' href='/icon-192x192.svg' type='image/svg+xml' />
        <link rel='apple-touch-icon' href='/apple-touch-icon.svg' />
        <meta name='apple-mobile-web-app-capable' content='yes' />
        <meta name='apple-mobile-web-app-status-bar-style' content='default' />
        <meta name='apple-mobile-web-app-title' content='GreenSteel' />
        <meta name='msapplication-TileColor' content='#3b82f6' />
        <meta name='theme-color' content='#3b82f6' />
        <meta name='application-name' content='GreenSteel' />
        <meta name='msapplication-TileImage' content='/icon-192x192.svg' />

        {/* PWA 관련 메타데이터 */}
        <meta name='mobile-web-app-capable' content='yes' />
        <meta name='apple-mobile-web-app-capable' content='yes' />
        <meta
          name='apple-mobile-web-app-status-bar-style'
          content='black-translucent'
        />
        <meta name='apple-mobile-web-app-title' content='GreenSteel' />
        <meta name='msapplication-TileColor' content='#3b82f6' />
        <meta name='msapplication-TileImage' content='/icon-192x192.svg' />
        <meta name='theme-color' content='#3b82f6' />
        <meta name='msapplication-config' content='/browserconfig.xml' />

        {/* iOS PWA 메타데이터 */}
        <meta name='apple-touch-fullscreen' content='yes' />
        <meta name='apple-mobile-web-app-orientations' content='portrait' />

        {/* Android PWA 메타데이터 */}
        <meta name='mobile-web-app-capable' content='yes' />
        <meta name='theme-color' content='#3b82f6' />
        <meta name='background-color' content='#0f172a' />
      </head>
      <body className={`${inter.className} antialiased`}>
        {/* Google tag (gtag.js) */}
        <Script
          src='https://www.googletagmanager.com/gtag/js?id=G-2GFHCRYLT8'
          strategy='afterInteractive'
        />
        <Script id='google-analytics' strategy='afterInteractive'>
          {`
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-2GFHCRYLT8');
          `}
        </Script>

        {/* Daum Postcode Service */}
        <Script
          src='//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js'
          strategy='afterInteractive'
        />

        {/* PWA Components */}
        <PWAServiceWorker />
        <OfflineIndicator />
        <PWAInstallBanner />

        {children}
      </body>
    </html>
  );
}
