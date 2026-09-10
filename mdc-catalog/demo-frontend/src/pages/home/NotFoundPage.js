import React from 'react';
import Link from 'next/link';
import Image from 'next/image';

const NotFoundPage = () => {

    return (
        <div className="surface-ground flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
            <div className="flex flex-column align-items-center justify-content-center">
                <Image
                    src="/layout/images/MaaSAI_colour_main_letters.png"
                    alt="MAASAI logo"
                    width={320}
                    height={72}
                    className="mb-5 flex-shrink-0"
                    priority
                />
                <div style={{ borderRadius: '56px', padding: '0.3rem', background: 'linear-gradient(180deg, rgba(33, 150, 243, 0.4) 10%, rgba(33, 150, 243, 0) 30%)' }}>
                    <div className="w-full surface-card py-8 px-5 sm:px-8 flex flex-column align-items-center" style={{ borderRadius: '53px' }}>
                        <span className="text-blue-500 font-bold text-3xl">404</span>
                        <h1 className="text-900 font-bold text-5xl mb-2">Not Found</h1>
                        <div className="text-600 mb-5">Requested resource is not available</div>
                        <Link href="/" className="w-full flex align-items-center py-5 border-300 border-bottom-1">
                            <span className="flex justify-content-center align-items-center bg-cyan-400 border-round" style={{ height: '3.5rem', width: '3.5rem' }}>
                                <i className="text-50 pi pi-fw pi-table text-2xl"></i>
                            </span>
                            <span className="ml-4 flex flex-column">
                                <span className="text-900 lg:text-xl font-medium mb-1">Back to main</span>
                                <span className="text-600 lg:text-lg">Go back to main.</span>
                            </span>
                        </Link>
                        <Link href="/home/AccessDenied" className="w-full flex align-items-center py-5 border-300 border-bottom-1">
                            <span className="flex justify-content-center align-items-center bg-orange-400 border-round" style={{ height: '3.5rem', width: '3.5rem' }}>
                                <i className="pi pi-fw pi-question-circle text-50 text-2xl"></i>
                            </span>
                            <span className="ml-4 flex flex-column">
                                <span className="text-900 lg:text-xl font-medium mb-1">Access Denied</span>
                                <span className="text-600 lg:text-lg">Access denied page example.</span>
                            </span>
                        </Link>
                        <Link href="/home/ErrorPage" className="w-full flex align-items-center mb-5 py-5 border-300 border-bottom-1">
                            <span className="flex justify-content-center align-items-center bg-indigo-400 border-round" style={{ height: '3.5rem', width: '3.5rem' }}>
                                <i className="pi pi-fw pi-unlock text-50 text-2xl"></i>
                            </span>
                            <span className="ml-4 flex flex-column">
                                <span className="text-900 lg:text-xl font-medium mb-1">Error Page</span>
                                <span className="text-600 lg:text-lg">Error page example.</span>
                            </span>
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
};

NotFoundPage.getLayout = function getLayout(page) {
    return (
        <React.Fragment>
            {page}
        </React.Fragment>
    );
};

export default NotFoundPage;