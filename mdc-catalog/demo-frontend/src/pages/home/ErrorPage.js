import { useRouter } from 'next/router';
import React from 'react';
import Image from 'next/image';
import { Button } from 'primereact/button';

const ErrorPage = () => {
    const router = useRouter();

    return (
        <div className="surface-ground flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
            <div className="flex flex-column align-items-center justify-content-center">
                <Image
                    src="/layout/images/MaaSAI_colour_main_letters.png"
                    alt="MaaSAI logo"
                    width={320}
                    height={72}
                    className="mb-5 flex-shrink-0"
                    priority
                />
                <div style={{ borderRadius: '56px', padding: '0.3rem', background: 'linear-gradient(180deg, rgba(33, 150, 243, 0.4) 10%, rgba(33, 150, 243, 0) 30%)' }}>
                    <div className="w-full surface-card py-8 px-5 sm:px-8 flex flex-column align-items-center" style={{ borderRadius: '53px' }}>
                        <div className="flex justify-content-center align-items-center orange-background border-circle" style={{ height: '3.2rem', width: '3.2rem' }}>
                            <i className="pi pi-fw pi-exclamation-circle text-2xl text-white"></i>
                        </div>
                        <h1 className="text-900 font-bold text-5xl mb-2">Error Occurred</h1>
                        <div className="text-600 mb-5">Something went wrong.</div>
                        <Image
                            src="/images/asset-error.svg"
                            alt="Error illustration"
                            width={480}
                            height={320}
                            className="mb-5"
                            style={{ width: '80%', height: 'auto' }}
                        />
                        <Button icon="pi pi-arrow-left" label="Go to Home" text onClick={() => router.push('/')} />
                    </div>
                </div>
            </div>
        </div>
    );
};

ErrorPage.getLayout = function getLayout(page) {
    return (
        <React.Fragment>
            {page}
            {/*<AppConfig />*/}
        </React.Fragment>
    );
};

export default ErrorPage;
