export const buildProviderPreviewPayload = (form) => {
    const cleanText = (value) => String(value ?? '').trim();

    const customOfferingFields = (form.customOfferingFields || [])
        .map((field) => ({
            name: cleanText(field.name),
            value: cleanText(field.value)
        }))
        .filter((field) => field.name && field.value);

    const customCapabilityFields = (form.customCapabilityFields || [])
        .map((field) => ({
            name: cleanText(field.name),
            value: cleanText(field.value),
            unit: cleanText(field.unit),
            notes: cleanText(field.notes)
        }))
        .filter((field) => field.name && field.value)
        .map((field) => Object.fromEntries(
            Object.entries(field).filter(([, value]) => value !== '')
        ));

    if (form.action === 'register_provider') {
        return {
            action: form.action,
            provider_id: form.providerId,
            provider_name: form.providerName,
            country: form.country,
            description: form.description,
            offerings: [
                {
                    offering_id: form.offeringId,
                    offering_name: form.offeringName,
                    custom_offering_fields: customOfferingFields,
                    capabilities: {
                        custom_capability_fields: customCapabilityFields
                    }
                }
            ]
        };
    }

    const splitList = (value) => String(value || '')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);

    const commonCapabilities = {
        materials: form.materials,
        available_grades: form.availableGrades,
        processes: form.processes,
        certifications: form.certifications,
        batch_size: {
            min: form.batchSizeMin,
            max: form.batchSizeMax
        },
        lead_time_weeks: {
            min: form.leadTimeMinWeeks,
            max: form.leadTimeMaxWeeks
        },
        weight_kg: { max: form.weightMaxKg },
        notes: form.capabilityNotes
    };

    const capabilityByTemplate = {
        gear_manufacturing: {
            module: {
                min: form.moduleMin,
                max: form.moduleMax
            },
            outside_diameter_mm: {
                min: form.diameterMinMm,
                max: form.diameterMaxMm
            },
            quality: {
                standard: form.qualityStandard,
                class: form.qualityClass
            }
        },
        shaft_manufacturing: {
            length_mm: { max: form.lengthMaxMm },
            outer_diameter_mm: {
                min: form.outerDiameterMinMm,
                max: form.outerDiameterMaxMm
            },
            spline_module: { exact: form.splineModule }
        },
        metal_part_manufacturing: {
            maximum_dimensions_mm: {
                length: form.maxLengthMm,
                width: form.maxWidthMm,
                height_or_thickness: form.maxHeightMm,
                diameter: form.maxDiameterMm
            },
            tolerance: form.tolerance,
            surface_finish: form.surfaceFinish
        },
        general_precision_manufacturing: {
            capability_description: form.capabilityDescription,
            supported_keywords: splitList(form.partTypeKeywords),
            maximum_size: form.maximumSizeDescription
        }
    };

    const capabilities = {
        ...(capabilityByTemplate[form.capabilityTemplate] || capabilityByTemplate.gear_manufacturing),
        ...commonCapabilities
    };

    const supportedPartTypes = form.capabilityTemplate === 'general_precision_manufacturing'
        ? splitList(form.partTypeKeywords)
        : form.partTypes;

    return {
        action: form.action,
        provider_id: form.providerId,
        provider_name: form.providerName,
        country: form.country,
        description: form.description,
        publication_metadata: {
            source_type: 'provider_confirmed',
            confidence: 'declared'
        },
        certifications: form.certifications,
        offerings: [
            {
                offering_id: form.offeringId,
                offering_name: form.offeringName,
                service_category: form.serviceCategory,
                part_family: form.partFamily,
                capability_template: form.capabilityTemplate,
                supported_part_types: supportedPartTypes,
                support_status: form.supportStatus,
                capabilities
            }
        ]
    };
};
