import React from 'react';
import { Button } from 'primereact/button';

export default function MaaSAIButton({ className, ...props }) {
    return <Button {...props} className={className ? 'maasai-button ' + className : 'maasai-button'} />;
}
