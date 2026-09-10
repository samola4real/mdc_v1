import React from 'react';
import NotFoundPage from '@/pages/home/NotFoundPage';

const Custom404 = () => {
    return <NotFoundPage />;
};

Custom404.getLayout = function getLayout(page) {
    return page;
};

export default Custom404;
