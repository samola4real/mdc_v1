import { jsPDF } from 'jspdf';

const fontFile = 'DejaVuSans.ttf';
const navy = '#223F61';
const orange = '#E78C3A';
const ink = '#262626';
const muted = '#4C5A68';
const pale = '#F2F4F7';

export const offeringPdfFilename = (offeringId) => {
    const name = offeringId.replace(/[^a-zA-Z0-9_-]+/g, '_').slice(0, 120) || 'manufacturing_offering';
    const reserved = /^(?:con|prn|aux|nul|com[1-9]|lpt[1-9])$/i.test(name);
    return (reserved ? 'offering_' + name : name) + '.pdf';
};

let fontRequest;
const loadFont = () => {
    if (!fontRequest) {
        fontRequest = fetch('/layout/fonts/offering-pdf/' + fontFile)
            .then(async (response) => {
                if (!response.ok) throw new Error('Offering PDF font is unavailable.');
                const bytes = new Uint8Array(await response.arrayBuffer());
                const chunks = [];
                for (let i = 0; i < bytes.length; i += 16384) {
                    chunks.push(String.fromCharCode(...bytes.subarray(i, i + 16384)));
                }
                return btoa(chunks.join(''));
            }).catch((error) => {
                fontRequest = undefined;
                throw error;
            });
    }
    return fontRequest;
};

export function buildOfferingPdf(details, comparison, font, referenceDate = new Date()) {
    const doc = new jsPDF({ unit: 'mm', format: 'a4', compress: true, putOnlyUsedFonts: true });
    doc.addFileToVFS(fontFile, font);
    doc.addFont(fontFile, 'OfferingSans', 'normal');
    doc.setFont('OfferingSans');
    const fontMetadata = doc.getFont().metadata;
    doc.setProperties({ title: 'Manufacturing Offering', subject: 'MaaS Dynamic Catalogue' });
    doc.setCreationDate(referenceDate);

    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 17;
    const width = pageWidth - 2 * margin;
    const bottom = pageHeight - 21;
    let y;

    const text = (value, x, baseline, size, color = ink) => {
        doc.setFontSize(size).setTextColor(color).text(value, x, baseline);
    };
    const band = (first) => {
        const height = first ? 30 : 22;
        doc.setFillColor(navy).rect(0, 0, pageWidth, height, 'F');
        doc.setFillColor(orange).rect(0, height, pageWidth, 1.5, 'F');
        text('MaaS Dynamic Catalogue', margin, 9, 10, '#FFFFFF');
        text('Manufacturing Offering', margin, first ? 23 : 17, first ? 24 : 14, '#FFFFFF');
        y = height + 9;
    };
    const newPage = () => {
        doc.addPage();
        band(false);
    };
    const ensureRoom = (height) => {
        if (y + height > bottom) newPage();
    };
    const split = (value, size, maxWidth) => {
        const normalized = (value || '').normalize('NFC');
        for (const character of new Set(normalized)) {
            if (!/\s/u.test(character) && !fontMetadata.characterToGlyph(character.codePointAt(0))) {
                throw Object.assign(new Error('Missing glyph in offering PDF font.'), { code: 'unsupported_pdf_characters' });
            }
        }
        doc.setFontSize(size);
        return doc.splitTextToSize(normalized, maxWidth);
    };
    const paragraph = (value, size, step, color) => {
        for (const line of split(value, size, width)) {
            ensureRoom(step);
            text(line, margin, y + step - 1.6, size, color);
            y += step;
        }
    };
    const heading = (title) => {
        ensureRoom(32);
        y += 3;
        paragraph(title, 15, 7, navy);
        doc.setDrawColor(orange).setLineWidth(0.45).line(margin, y + 1, margin + width, y + 1);
        y += 5;
    };
    const table = (rows, columns, headers, continuation) => {
        const size = 10;
        const leading = 4.6;
        const inset = 2.3;
        const header = () => {
            if (!headers) return;
            doc.setFillColor(pale).rect(margin, y, width, 8, 'F');
            let left = margin;
            headers.forEach((label, index) => {
                text(label, left + inset, y + 5.2, 9.5, navy);
                left += columns[index];
            });
            y += 8;
        };
        const nextTablePage = () => {
            newPage();
            if (continuation) paragraph(continuation, 12, 6, navy);
            header();
        };
        header();
        rows.forEach((cells) => {
            const lines = cells.map((cell, index) => split(cell, size, columns[index] - 2 * inset));
            const count = Math.max(...lines.map((column) => column.length));
            const area = count * leading + 3;
            if (area <= bottom - 45 && y + area > bottom) nextTablePage();
            let offset = 0;
            while (offset < count) {
                let room = Math.floor((bottom - y - 3) / leading);
                if (room < 1) {
                    nextTablePage();
                    room = Math.floor((bottom - y - 3) / leading);
                }
                const shown = Math.min(room, count - offset);
                let left = margin;
                lines.forEach((column, index) => {
                    column.slice(offset, offset + shown).forEach((line, lineIndex) => {
                        text(line, left + inset, y + 4.1 + lineIndex * leading, size, index === 0 ? navy : ink);
                    });
                    left += columns[index];
                });
                y += shown * leading + 3;
                doc.setDrawColor('#DDE3EA').setLineWidth(0.2).line(margin, y, margin + width, y);
                offset += shown;
            }
        });
        y += 3;
    };

    band(true);
    paragraph(details.providerName, 19, 8.8, navy);
    paragraph(details.offeringName, 14, 7.2, ink);
    const date = new Intl.DateTimeFormat('en-GB', { dateStyle: 'long' }).format(referenceDate);
    paragraph('Reference date · ' + date, 10, 5, muted);
    y += 3;
    heading('Requirement Comparison');
    table(comparison.map(({ label, requested, provided, status }) => [label, requested, provided, status]),
        [42, 44, width - 42 - 44 - 30, 30], ['Specification', 'Your requirement', 'Provider capability', 'Status'], 'Requirement Comparison');
    if (comparison.some(({ label }) => label === 'Material alternative')) {
        paragraph('One supported alternative satisfies the material preference.', 10, 5, muted);
    }
    if (comparison.length === 1) paragraph('No additional requirements were specified.', 10, 5, muted);
    y += 4;
    heading('Manufacturing Capability Overview');
    paragraph('Published capabilities', 10, 5, muted);
    for (const { title, rows } of details.sections) {
        ensureRoom(18);
        y += 3;
        paragraph(title, 12, 6, navy);
        if (rows.every(({ value }) => !value)) {
            table(rows.map(({ label }) => [label]), [width], null, title);
        } else {
            table(rows.map(({ label, value }) => [label, value]), [59, width - 59], null, title);
        }
    }

    const total = doc.getNumberOfPages();
    for (let page = 1; page <= total; page += 1) {
        doc.setPage(page);
        doc.setDrawColor('#DDE3EA').setLineWidth(0.2).line(margin, bottom + 5, margin + width, bottom + 5);
        text('MaaS Dynamic Catalogue', margin, bottom + 10, 9, muted);
        doc.setFontSize(9).setTextColor(muted).text(`Page ${page} of ${total}`, pageWidth - margin, bottom + 10, { align: 'right' });
    }
    return doc;
}

export const createOfferingPdf = async (details, comparison) => buildOfferingPdf(details, comparison, await loadFont());
