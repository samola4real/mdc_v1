import Document, { Head, Html, Main, NextScript } from 'next/document';

/*
    This is the _document.js file. It is only rendered on the server side and not on the client side.
    Event handlers like onClick can't be added to this file because it is only rendered on the server side.
    This file is useful for meta tags, links to external stylesheets, etc. It is to say, it is useful to edit
    html structure and tags that are not related to React.
 */
class MyDocument extends Document {
    static async getInitialProps(ctx) {
        const initialProps = await Document.getInitialProps(ctx);
        return { ...initialProps };
    }

    render() {
        return (
            <Html lang="en">
                <Head>
                    {/* ThemeContext swaps href at runtime via id="theme-css".
                        Avoid FOUC by inlining the chosen theme as early as possible. */}
                    <script
                        // eslint-disable-next-line react/no-danger
                        dangerouslySetInnerHTML={{
                            __html: `(function(){try{var t=localStorage.getItem('maasai.theme');if(t==='dark'||t==='hmi'){document.documentElement.setAttribute('data-theme',t);}}catch(e){}})();`
                        }}
                    />
                    <link id="theme-css" href="/themes/lara-light-indigo/theme.css" rel="stylesheet" />
                    <link rel="preconnect" href="https://fonts.googleapis.com" />
                    <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
                    <link
                        href="https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700;800&display=swap"
                        rel="stylesheet"
                    />
                </Head>
                <body>
                    <Main />
                    <NextScript />
                </body>
            </Html>
        );
    }
}

export default MyDocument;
