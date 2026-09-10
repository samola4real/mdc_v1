import React, { useMemo, useRef, useState } from "react";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { InputNumber } from "primereact/inputnumber";
import { InputText } from "primereact/inputtext";
import { Message } from "primereact/message";
import { MultiSelect } from "primereact/multiselect";
import { Panel } from "primereact/panel";
import { Toast } from "primereact/toast";
import { getProviderDemoState } from "@/services/mdc/demoAdmin.service";
import { searchServiceDiscovery } from "@/services/mdc/search.service";
import SearchErrorMessage from "./SearchErrorMessage";
import SearchPayloadPreview from "./SearchPayloadPreview";
import SearchResultsList from "./SearchResultsList";
import {
  certifications,
  materials,
  metalPartTypeOptions,
  partFamilies,
  partTypes,
  processes,
} from "./mockData";

const normalizeFamily = (family) => {
  if (family === "gear") return "gear";
  if (family === "shaft") return "shaft";
  if (family === "metal_part") return "metal_part";
  return family;
};

const toBackendFamily = (family) => normalizeFamily(family);

const serviceCategoryByFamily = {
  gear: "precision_gears",
  shaft: "precision_shafts",
  metal_part: "precision_metal_parts",
};

const acceptedMetalPartTypes = new Set([
  "block",
  "plate",
  "bracket",
  "bushing",
  "roller",
  "collar",
]);

const getServiceCategoryForFamily = (family) =>
  serviceCategoryByFamily[normalizeFamily(family)] || serviceCategoryByFamily.gear;

const getPartTypeForFamily = (family, partType) => {
  if (normalizeFamily(family) === "metal_part") {
    return acceptedMetalPartTypes.has(partType) ? partType : "block";
  }

  return partType;
};

const exactNumber = (value) => (value == null ? undefined : { exact: value });

const maxNumber = (value) => (value == null ? undefined : { max: value });

const positiveNumber = (value) => {
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : undefined;
};

const positiveMaxNumber = (value) => {
  const number = positiveNumber(value);
  return number == null ? undefined : { max: number };
};

const cleanObject = (value) =>
  Object.fromEntries(
    Object.entries(value).filter(
      ([, item]) => item !== undefined && item !== null && item !== ""
    )
  );

const buildGenericRequirements = (form, extraRequirements = {}) =>
  cleanObject({
    materials: form.material ? [form.material] : undefined,
    processes: form.processes?.length ? form.processes : undefined,
    certifications: form.certification ? [form.certification] : undefined,
    ...extraRequirements,
  });

const toArray = (value) => {
  if (Array.isArray(value)) return value;
  if (value && typeof value === "object") return Object.values(value);
  return value == null || value === "" ? [] : [value];
};

const normalizeSearchText = (value) =>
  String(value || "")
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const getResultsArray = (response) => {
  if (Array.isArray(response)) return response;
  if (Array.isArray(response?.results)) return response.results;
  if (Array.isArray(response?.data?.results)) return response.data.results;
  return [];
};

const getProviderStateEntries = (state) => {
  const providers =
    state?.providers ||
    state?.state?.providers ||
    state?.demo_state?.providers ||
    state?.data?.providers;

  return providers ? toArray(providers) : toArray(state);
};

const getCustomFieldValue = (fields, names) => {
  const targets = toArray(names).map(normalizeSearchText);
  return toArray(fields).find((field) =>
    targets.includes(normalizeSearchText(field?.name))
  )?.value;
};

const customFieldRows = (fields) =>
  toArray(fields)
    .map((field, index) => ({
      id: `${field?.name || "field"}-${index}`,
      name: field?.name || "Field",
      value: [field?.value, field?.unit].filter(Boolean).join(" "),
      notes: field?.notes || "",
    }))
    .filter((field) => field.value || field.notes);

const getPayloadTerms = (payload) => {
  const generic = payload?.requirements?.generic_requirements || {};
  const terms = [
    payload?.service_category,
    payload?.part_family,
    payload?.part_type,
    ...toArray(generic.materials),
    ...toArray(generic.processes),
    ...toArray(generic.certifications),
  ];

  if (payload?.part_family === "metal_part") {
    terms.push("metal", "metal part", "precision metal");
  }

  return Array.from(new Set(terms.map(normalizeSearchText).filter(Boolean)));
};

const getPayloadDomainTerms = (payload) => {
  const terms = [payload?.service_category, payload?.part_family, payload?.part_type];

  if (payload?.part_family === "metal_part") {
    terms.push("metal", "metal part", "precision metal");
  }

  return Array.from(new Set(terms.map(normalizeSearchText).filter(Boolean)));
};

const extractOfferingValue = (offering, keys, customNames, customFields) => {
  const direct = toArray(keys).map((key) => offering?.[key]).find(Boolean);
  return direct || getCustomFieldValue(customFields, customNames);
};

const extractSupportedPartTypes = (offering, capabilityFields) => {
  const direct = [
    ...toArray(offering?.supported_part_types),
    ...toArray(offering?.supportedPartTypes),
    ...toArray(offering?.part_types),
  ];
  const custom = toArray(
    getCustomFieldValue(capabilityFields, [
      "Supported part type",
      "Supported part types",
      "Part type",
      "Part types",
    ])
  )
    .flatMap((value) => String(value).split(/[,;/]/))
    .map((value) => value.trim());

  return [...direct, ...custom].filter(Boolean);
};

const normalizeProviderId = (result) =>
  String(
    result?.provider_id ||
      result?.providerId ||
      result?.provider?.provider_id ||
      result?.provider?.id ||
      ""
  ).toLowerCase();

const buildDemoResult = ({
  provider,
  providerPayload,
  offering,
  payload,
  matchedFields,
  customOfferingFields,
  customCapabilityFields,
}) => {
  const capabilities = offering?.capabilities || {};
  const providerId =
    providerPayload?.provider_id ||
    providerPayload?.providerId ||
    providerPayload?.id ||
    provider?.provider_id ||
    provider?.id ||
    "demo_provider";
  const providerName =
    providerPayload?.provider_name ||
    providerPayload?.providerName ||
    providerPayload?.name ||
    providerId;
  const offeringId =
    offering?.offering_id ||
    offering?.offeringId ||
    offering?.id ||
    `${providerId}_demo_offering`;
  const offeringName =
    offering?.offering_name ||
    offering?.offeringName ||
    offering?.name ||
    offeringId;
  const generic = payload?.requirements?.generic_requirements || {};
  const materials = [
    ...toArray(capabilities?.materials),
    ...toArray(getCustomFieldValue(customCapabilityFields, "Material")),
  ].filter(Boolean);
  const processes = [
    ...toArray(capabilities?.processes),
    ...toArray(getCustomFieldValue(customCapabilityFields, "Process")),
  ].filter(Boolean);
  const certifications = [
    ...toArray(providerPayload?.certifications),
    ...toArray(capabilities?.certifications),
    ...toArray(getCustomFieldValue(customCapabilityFields, "Certification")),
  ].filter(Boolean);

  return {
    provider_id: providerId,
    provider_name: providerName,
    offering_id: offeringId,
    offering_name: offeringName,
    part_type: payload?.part_type,
    status: "matched",
    match: { status: "matched" },
    matched_attributes: [
      {
        field: "part_type",
        requested: payload?.part_type,
        provided: { support_status: "confirmed" },
        status: "confirmed",
      },
      ...matchedFields.map((field) => ({
        field: "demo_field",
        requested: field,
        provided: "Demo registration",
        status: "confirmed",
      })),
    ],
    evidence: {
      materials,
      certifications,
      generic_capabilities: {
        materials,
        processes,
      },
      family_capabilities: {},
    },
    demo_overlay: {
      source: "Demo registered provider",
      country: providerPayload?.country || provider?.country || "",
      description: providerPayload?.description || provider?.description || "",
      reason:
        matchedFields.length > 0
          ? `Matched demo fields: ${matchedFields.join(", ")}`
          : "This provider was registered in the demo provider workflow and matches the current search terms.",
      customOfferingFields: customFieldRows(customOfferingFields),
      customCapabilityFields: customFieldRows(customCapabilityFields),
    },
  };
};

const buildDemoOverlayResults = (state, payload, backendResults) => {
  const existingProviderIds = new Set(backendResults.map(normalizeProviderId).filter(Boolean));
  const searchTerms = getPayloadTerms(payload);
  const domainTerms = getPayloadDomainTerms(payload);
  const providers = getProviderStateEntries(state);

  return providers.flatMap((provider) => {
    const providerPayload = provider?.payload || provider?.provider || provider;
    const providerId =
      providerPayload?.provider_id ||
      providerPayload?.providerId ||
      providerPayload?.id ||
      provider?.provider_id ||
      provider?.id ||
      "";

    if (providerId && existingProviderIds.has(String(providerId).toLowerCase())) {
      return [];
    }

    return toArray(providerPayload?.offerings).flatMap((offering) => {
      const customOfferingFields = offering?.custom_offering_fields || [];
      const capabilities = offering?.capabilities || {};
      const customCapabilityFields = capabilities?.custom_capability_fields || [];
      const serviceCategory = extractOfferingValue(
        offering,
        ["service_category", "serviceCategory"],
        ["Service category", "service_category"],
        customOfferingFields
      );
      const partFamily = extractOfferingValue(
        offering,
        ["part_family", "partFamily"],
        ["Part family", "Supported part family", "part_family"],
        customOfferingFields
      );
      const supportedPartTypes = extractSupportedPartTypes(offering, customCapabilityFields);
      const controlledMatches = [
        normalizeSearchText(serviceCategory) === normalizeSearchText(payload?.service_category)
          ? payload?.service_category
          : null,
        normalizeSearchText(partFamily) === normalizeSearchText(payload?.part_family)
          ? payload?.part_family
          : null,
        supportedPartTypes.map(normalizeSearchText).includes(normalizeSearchText(payload?.part_type))
          ? payload?.part_type
          : null,
      ].filter(Boolean);
      const textBlob = normalizeSearchText([
        providerPayload?.provider_name,
        providerPayload?.providerName,
        providerPayload?.name,
        providerPayload?.description,
        offering?.offering_name,
        offering?.offeringName,
        offering?.name,
        offering?.description,
        ...customOfferingFields.flatMap((field) => [field?.name, field?.value]),
        ...customCapabilityFields.flatMap((field) => [
          field?.name,
          field?.value,
          field?.unit,
          field?.notes,
        ]),
      ].filter(Boolean).join(" "));
      const domainTextMatches = domainTerms.filter((term) => textBlob.includes(term));
      const textMatches =
        controlledMatches.length > 0 || domainTextMatches.length > 0
          ? searchTerms.filter((term) => textBlob.includes(term))
          : [];
      const matchedFields = Array.from(
        new Set([...controlledMatches, ...domainTextMatches, ...textMatches])
      );

      if (matchedFields.length === 0) {
        return [];
      }

      return [
        buildDemoResult({
          provider,
          providerPayload,
          offering,
          payload,
          matchedFields,
          customOfferingFields,
          customCapabilityFields,
        }),
      ];
    });
  });
};

const metalPartTypeLabels = {
  block: "Block technical fields",
  bracket: "Bracket technical fields",
  plate: "Plate technical fields",
  bushing: "Bushing technical fields",
  roller: "Roller technical fields",
  collar: "Collar technical fields",
};

const parseQuality = (value) => {
  if (!value || typeof value !== "string") {
    return undefined;
  }

  const [standard, rawClass] = value.trim().split(/\s+/);
  const maxClass = Number(rawClass);

  if (!standard || !Number.isFinite(maxClass) || maxClass <= 0) {
    return undefined;
  }

  return {
    standard,
    max_class: maxClass,
  };
};

const buildBoundingBox = (form, heightValue = form.metalHeightMm) =>
  cleanObject({
    length_mm: maxNumber(form.metalLengthMm),
    width_mm: maxNumber(form.metalWidthMm),
    height_mm: maxNumber(heightValue),
  });

const buildMetalPartRequirements = (form) => {
  const partType = getPartTypeForFamily("metal_part", form.partType);
  const genericRequirements = buildGenericRequirements(form, {
    weight_kg: positiveNumber(form.metalWeightKg),
    surface_finish_ra_um: positiveMaxNumber(form.surfaceFinish),
  });

  if (partType === "bracket") {
    return {
      partFamilySpecifications: cleanObject({
        bounding_box_mm: buildBoundingBox(form),
      }),
      partTypeSpecifications: cleanObject({
        vertical_flange_length_mm: maxNumber(form.flangeLengthMm),
        horizontal_flange_length_mm: maxNumber(form.horizontalFlangeLengthMm),
      }),
      genericRequirements: buildGenericRequirements(form, {
        weight_kg: positiveNumber(form.metalWeightKg),
        tolerance_mm: maxNumber(form.toleranceMm),
        surface_finish_ra_um: positiveMaxNumber(form.surfaceFinish),
      }),
    };
  }

  if (partType === "plate") {
    return {
      partFamilySpecifications: cleanObject({
        bounding_box_mm: buildBoundingBox(form, form.metalThicknessMm),
      }),
      partTypeSpecifications: cleanObject({
        number_of_holes: maxNumber(form.mountingHolesCount),
      }),
      genericRequirements: buildGenericRequirements(form, {
        weight_kg: positiveNumber(form.metalWeightKg),
        tolerance_mm: maxNumber(form.toleranceMm),
        surface_finish_ra_um: positiveMaxNumber(form.surfaceFinish),
      }),
    };
  }

  if (partType === "bushing") {
    return {
      partFamilySpecifications: cleanObject({
        inner_diameter_mm: maxNumber(form.metalInnerDiameterMm),
        outer_diameter_mm: maxNumber(form.metalOuterDiameterMm),
        overall_length_mm: maxNumber(form.metalLengthMm),
        tolerance_mm: maxNumber(form.toleranceMm),
      }),
      partTypeSpecifications: cleanObject({
        flange_diameter_mm: maxNumber(form.flangeDiameterMm),
      }),
      genericRequirements,
    };
  }

  if (partType === "roller") {
    return {
      partFamilySpecifications: cleanObject({
        inner_diameter_mm: maxNumber(form.shaftOrBoreDiameterMm),
        outer_diameter_mm: maxNumber(form.metalOuterDiameterMm),
        overall_length_mm: maxNumber(form.metalLengthMm),
        tolerance_mm: maxNumber(form.toleranceMm),
      }),
      partTypeSpecifications: {},
      genericRequirements,
    };
  }

  if (partType === "collar") {
    return {
      partFamilySpecifications: cleanObject({
        inner_diameter_mm: maxNumber(form.boreDiameterMm),
        outer_diameter_mm: maxNumber(form.metalOuterDiameterMm),
        overall_length_mm: maxNumber(form.metalLengthMm),
        tolerance_mm: maxNumber(form.toleranceMm),
      }),
      partTypeSpecifications: {},
      genericRequirements,
    };
  }

  return {
    partFamilySpecifications: cleanObject({
      bounding_box_mm: buildBoundingBox(form),
    }),
    partTypeSpecifications: cleanObject({
      number_of_holes: maxNumber(form.mountingHolesCount),
    }),
    genericRequirements: buildGenericRequirements(form, {
      weight_kg: positiveNumber(form.metalWeightKg),
      tolerance_mm: maxNumber(form.toleranceMm),
      surface_finish_ra_um: positiveMaxNumber(form.surfaceFinish),
    }),
  };
};

const buildSearchPayload = (form) => {
  const partFamily = toBackendFamily(form.partFamily);
  const partType = getPartTypeForFamily(partFamily, form.partType);
  const isShaft = partFamily === "shaft";
  const isGear = partFamily === "gear";
  const isMetalPart = partFamily === "metal_part";
  const metalPartRequirements = isMetalPart
    ? buildMetalPartRequirements(form)
    : null;
  const partFamilySpecifications = isShaft
    ? cleanObject({
        length_mm: maxNumber(form.lengthMm),
        outer_diameter_mm: maxNumber(form.outerDiameterMm),
        tolerance_mm: maxNumber(form.toleranceMm),
      })
    : isGear
    ? cleanObject({
        module: exactNumber(form.module),
        diametral_pitch:
          form.diametralPitch == null
            ? undefined
            : { min: form.diametralPitch, max: form.diametralPitch },
        outside_diameter_mm: maxNumber(form.outsideDiameterMm),
        gear_quality: parseQuality(form.gearQuality),
        tolerance_mm: maxNumber(form.toleranceMm),
      })
    : isMetalPart
    ? metalPartRequirements.partFamilySpecifications
    : {};
  const partTypeSpecifications = isShaft
    ? cleanObject({
        spline_module:
          form.partType === "splined_shaft"
            ? exactNumber(form.splineModule)
            : undefined,
        inner_diameter_mm:
          form.partType === "hollow_shaft"
            ? maxNumber(form.internalDiameterMm)
            : undefined,
        wall_thickness_mm:
          form.partType === "hollow_shaft"
            ? exactNumber(form.wallThicknessMm)
            : undefined,
      })
    : isGear
    ? cleanObject({
        face_width_mm: exactNumber(form.faceWidthMm),
      })
    : isMetalPart
    ? metalPartRequirements.partTypeSpecifications
    : {};
  const genericRequirements = isMetalPart
    ? metalPartRequirements.genericRequirements
    : buildGenericRequirements(form);

  return cleanObject({
    request_id: form.requestId,
    consumer_id: form.consumerId,
    service_category: getServiceCategoryForFamily(partFamily),
    part_family: partFamily,
    part_type: partType || undefined,
    requirements: {
      part_family_specifications: partFamilySpecifications,
      part_type_specifications: partTypeSpecifications,
      generic_requirements: genericRequirements,
    },
    match_policy: {
      unknown_policy: "keep_as_unknown",
      optional_match_mode: "score_only",
      minimum_score: null,
    },
  });
};

const ConsumerSearchMockup = () => {
  const toast = useRef(null);
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [demoProviderWarning, setDemoProviderWarning] = useState(null);
  const [form, setForm] = useState({
    consumerId: "consumer_demo_001",
    requestId: `req-demo-${Date.now()}`,
    partFamily: "gear",
    partType: "spur_gear",
    material: "alloyed_carburizing_steel",
    processes: ["hobbing", "turn_mill"],
    certification: "ISO9001_2015",
    requirement: "Evidence-backed supplier for precision gear manufacturing",
    module: 2.0,
    diametralPitch: 10,
    outsideDiameterMm: 100,
    gearQuality: "DIN 6",
    faceWidthMm: 25,
    lengthMm: 220,
    outerDiameterMm: 35,
    splineModule: 1.5,
    internalDiameterMm: 12,
    wallThicknessMm: 6,
    metalLengthMm: 150,
    metalWidthMm: 80,
    metalHeightMm: 20,
    metalThicknessMm: 8,
    metalDiameterMm: 50,
    metalInnerDiameterMm: 20,
    metalOuterDiameterMm: 50,
    metalWallThicknessMm: 5,
    metalWeightKg: 2.5,
    flangeLengthMm: 40,
    horizontalFlangeLengthMm: 40,
    flangeDiameterMm: 60,
    mountingHolesCount: 4,
    holeDiameterMm: 8,
    shaftOrBoreDiameterMm: 15,
    boreDiameterMm: 20,
    materialGrade: "Customer specified",
    surfaceFinish: "Customer specified",
    holesOrCutouts: "",
    holesOrBores: "",
    pocketsOrSlots: "",
    cutoutDetails: "",
    keywayRequired: "",
    threadRequired: "",
    setScrewRequired: "",
    partDescription: "",
    mainDimensions: "",
    customProcess: "",
    drawingAvailable: "",
    additionalRequirements: "",
    toleranceMm: 0.02,
  });

  const normalizedPartFamily = normalizeFamily(form.partFamily);
  const isMetalPart = normalizedPartFamily === "metal_part";
  const availablePartTypes =
    normalizedPartFamily === "shaft"
      ? partTypes.shafts
      : normalizedPartFamily === "gear"
      ? partTypes.gears
      : metalPartTypeOptions;
  const payload = useMemo(() => buildSearchPayload(form), [form]);

  const setField = (field, value) =>
    setForm((current) => ({ ...current, [field]: value }));

  const handlePartFamilyChange = (value) => {
    const family = normalizeFamily(value);
    const defaults = {
      gear: {
        partType: "spur_gear",
      },
      shaft: {
        partType: "splined_shaft",
      },
      metal_part: {
        partType: "block",
      },
    };
    const nextDefaults = defaults[family] || defaults.gear;

    setForm((current) => ({
      ...current,
      partFamily: family,
      partType: nextDefaults.partType,
    }));
  };

  const search = async () => {
    setError(null);
    setResponse(null);
    setDemoProviderWarning(null);
    setLoading(true);

    try {
      const result = await searchServiceDiscovery(payload);
      const backendResults = getResultsArray(result);
      let demoResults = [];
      let nextDemoWarning = null;

      try {
        const demoState = await getProviderDemoState();
        demoResults = buildDemoOverlayResults(demoState, payload, backendResults);
      } catch (demoError) {
        nextDemoWarning = "Demo registered providers could not be loaded.";
      }

      setDemoProviderWarning(nextDemoWarning);
      setResponse({
        ...(Array.isArray(result) ? { results: result } : result),
        results: [...backendResults, ...demoResults],
        demo_overlay: {
          backend_count: backendResults.length,
          demo_count: demoResults.length,
          warning: nextDemoWarning,
        },
      });
      toast.current?.show({
        severity: "success",
        summary: "Search completed",
        detail: "MDC search response received.",
        life: 2500,
      });
    } catch (nextError) {
      setError(nextError);
      toast.current?.show({
        severity: "error",
        summary: "Search failed",
        detail: nextError?.message || "MDC search request failed.",
        life: 3500,
      });
    } finally {
      setLoading(false);
    }
  };

  const renderNumberField = (id, label, field, props = {}) => (
    <div className="field col-12 md:col-3">
      <label htmlFor={id} className="font-medium">
        {label}
      </label>
      <InputNumber
        inputId={id}
        value={form[field]}
        onValueChange={(e) => setField(field, e.value)}
        className="w-full"
        {...props}
      />
    </div>
  );

  const renderTextField = (id, label, field, className = "field col-12 md:col-3") => (
    <div className={className}>
      <label htmlFor={id} className="font-medium">
        {label}
      </label>
      <InputText
        id={id}
        value={form[field]}
        onChange={(e) => setField(field, e.target.value)}
        className="w-full"
      />
    </div>
  );

  const renderMetalPartFields = () => {
    const mm = { suffix: " mm" };
    const kg = { suffix: " kg" };
    const tolerance = {
      minFractionDigits: 2,
      maxFractionDigits: 3,
      suffix: " mm",
    };

    if (form.partType === "bracket") {
      return (
        <div className="grid formgrid">
          {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
          {renderNumberField("metalWidthMm", "Width mm", "metalWidthMm", mm)}
          {renderNumberField("metalHeightMm", "Height mm", "metalHeightMm", mm)}
          {renderNumberField("flangeLengthMm", "Vertical flange length mm", "flangeLengthMm", mm)}
          {renderNumberField("horizontalFlangeLengthMm", "Horizontal flange length mm", "horizontalFlangeLengthMm", mm)}
          {renderNumberField("metalWeightKg", "Weight kg", "metalWeightKg", kg)}
          {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
          {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
        </div>
      );
    }

    if (form.partType === "plate") {
      return (
        <div className="grid formgrid">
          {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
          {renderNumberField("metalWidthMm", "Width mm", "metalWidthMm", mm)}
          {renderNumberField("metalThicknessMm", "Thickness mm", "metalThicknessMm", mm)}
          {renderNumberField("mountingHolesCount", "Number of holes", "mountingHolesCount")}
          {renderNumberField("metalWeightKg", "Weight kg", "metalWeightKg", kg)}
          {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
          {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
        </div>
      );
    }

    if (form.partType === "bushing") {
      return (
        <div className="grid formgrid">
          {renderNumberField("metalInnerDiameterMm", "Inner diameter mm", "metalInnerDiameterMm", mm)}
          {renderNumberField("metalOuterDiameterMm", "Outer diameter mm", "metalOuterDiameterMm", mm)}
          {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
          {renderNumberField("flangeDiameterMm", "Flange diameter mm", "flangeDiameterMm", mm)}
          {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
          {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
        </div>
      );
    }

    if (form.partType === "roller") {
      return (
        <div className="grid formgrid">
          {renderNumberField("metalOuterDiameterMm", "Outer diameter mm", "metalOuterDiameterMm", mm)}
          {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
          {renderNumberField("shaftOrBoreDiameterMm", "Inner diameter mm", "shaftOrBoreDiameterMm", mm)}
          {renderNumberField("metalWeightKg", "Weight kg", "metalWeightKg", kg)}
          {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
          {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
        </div>
      );
    }

    if (form.partType === "collar") {
      return (
        <div className="grid formgrid">
          {renderNumberField("boreDiameterMm", "Inner diameter mm", "boreDiameterMm", mm)}
          {renderNumberField("metalOuterDiameterMm", "Outer diameter mm", "metalOuterDiameterMm", mm)}
          {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
          {renderNumberField("metalWeightKg", "Weight kg", "metalWeightKg", kg)}
          {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
          {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
        </div>
      );
    }

    return (
      <div className="grid formgrid">
        {renderNumberField("metalLengthMm", "Length mm", "metalLengthMm", mm)}
        {renderNumberField("metalWidthMm", "Width mm", "metalWidthMm", mm)}
        {renderNumberField("metalHeightMm", "Height mm", "metalHeightMm", mm)}
        {renderNumberField("mountingHolesCount", "Number of holes", "mountingHolesCount")}
        {renderNumberField("metalWeightKg", "Weight kg", "metalWeightKg", kg)}
        {renderNumberField("metalToleranceMm", "Tolerance mm", "toleranceMm", tolerance)}
        {renderTextField("surfaceFinish", "Surface finish", "surfaceFinish")}
      </div>
    );
  };

  return (
    <div className="flex flex-column gap-4">
      <Toast ref={toast} />
      <Card title="Consumer search request">
        <div className="grid formgrid">
          <div className="field col-12 md:col-6">
            <label htmlFor="consumerId" className="font-medium">
              Consumer ID
            </label>
            <InputText
              id="consumerId"
              value={form.consumerId}
              onChange={(e) => setField("consumerId", e.target.value)}
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-6">
            <label htmlFor="requestId" className="font-medium">
              Request ID
            </label>
            <InputText
              id="requestId"
              value={form.requestId}
              onChange={(e) => setField("requestId", e.target.value)}
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-4">
            <label htmlFor="partFamily" className="font-medium">
              Part family
            </label>
            <Dropdown
              inputId="partFamily"
              value={form.partFamily}
              options={partFamilies}
              optionLabel="label"
              optionValue="value"
              onChange={(e) => handlePartFamilyChange(e.value)}
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-4">
            <label htmlFor="partType" className="font-medium">
              Part type
            </label>
            <Dropdown
              inputId="partType"
              value={form.partType}
              options={availablePartTypes}
              onChange={(e) => setField("partType", e.value)}
              optionLabel={isMetalPart ? "label" : undefined}
              optionValue={isMetalPart ? "value" : undefined}
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-4">
            <label htmlFor="material" className="font-medium">
              Material
            </label>
            <Dropdown
              inputId="material"
              value={form.material}
              options={materials}
              onChange={(e) => setField("material", e.value)}
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-4">
            <label htmlFor="processes" className="font-medium">
              Processes
            </label>
            <MultiSelect
              inputId="processes"
              value={form.processes}
              options={processes}
              onChange={(e) => setField("processes", e.value)}
              display="chip"
              className="w-full"
            />
          </div>
          <div className="field col-12 md:col-4">
            <label htmlFor="certification" className="font-medium">
              Certification
            </label>
            <Dropdown
              inputId="certification"
              value={form.certification}
              options={certifications}
              onChange={(e) => setField("certification", e.value)}
              className="w-full"
            />
          </div>
          <div className="field col-12">
            <label htmlFor="requirement" className="font-medium">
              Technical requirements
            </label>
            <InputText
              id="requirement"
              value={form.requirement}
              onChange={(e) => setField("requirement", e.target.value)}
              className="w-full"
            />
          </div>
        </div>

        <Panel
          header={
            isMetalPart
              ? metalPartTypeLabels[form.partType] || "Metal-part technical fields"
              : normalizedPartFamily === "shaft"
              ? "Shaft technical fields"
              : "Gear technical fields"
          }
          className="mb-3"
        >
          {isMetalPart ? (
            renderMetalPartFields()
          ) : normalizedPartFamily === "shaft" ? (
            <div className="grid formgrid">
              <div className="field col-12 md:col-4">
                <label htmlFor="lengthMm" className="font-medium">
                  Length mm
                </label>
                <InputNumber
                  inputId="lengthMm"
                  value={form.lengthMm}
                  onValueChange={(e) => setField("lengthMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="outerDiameterMm" className="font-medium">
                  Outer diameter mm
                </label>
                <InputNumber
                  inputId="outerDiameterMm"
                  value={form.outerDiameterMm}
                  onValueChange={(e) => setField("outerDiameterMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="splineModule" className="font-medium">
                  Spline module
                </label>
                <InputNumber
                  inputId="splineModule"
                  value={form.splineModule}
                  onValueChange={(e) => setField("splineModule", e.value)}
                  minFractionDigits={1}
                  maxFractionDigits={2}
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="internalDiameterMm" className="font-medium">
                  Internal diameter mm
                </label>
                <InputNumber
                  inputId="internalDiameterMm"
                  value={form.internalDiameterMm}
                  onValueChange={(e) => setField("internalDiameterMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="wallThicknessMm" className="font-medium">
                  Wall thickness mm
                </label>
                <InputNumber
                  inputId="wallThicknessMm"
                  value={form.wallThicknessMm}
                  onValueChange={(e) => setField("wallThicknessMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="toleranceMm" className="font-medium">
                  Tolerance mm
                </label>
                <InputNumber
                  inputId="toleranceMm"
                  value={form.toleranceMm}
                  onValueChange={(e) => setField("toleranceMm", e.value)}
                  minFractionDigits={2}
                  maxFractionDigits={3}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
            </div>
          ) : (
            <div className="grid formgrid">
              <div className="field col-12 md:col-4">
                <label htmlFor="module" className="font-medium">
                  Module
                </label>
                <InputNumber
                  inputId="module"
                  value={form.module}
                  onValueChange={(e) => setField("module", e.value)}
                  minFractionDigits={1}
                  maxFractionDigits={2}
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="diametralPitch" className="font-medium">
                  Diametral pitch
                </label>
                <InputNumber
                  inputId="diametralPitch"
                  value={form.diametralPitch}
                  onValueChange={(e) => setField("diametralPitch", e.value)}
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="outsideDiameterMm" className="font-medium">
                  Outside diameter mm
                </label>
                <InputNumber
                  inputId="outsideDiameterMm"
                  value={form.outsideDiameterMm}
                  onValueChange={(e) => setField("outsideDiameterMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="gearQuality" className="font-medium">
                  Gear quality
                </label>
                <InputText
                  id="gearQuality"
                  value={form.gearQuality}
                  onChange={(e) => setField("gearQuality", e.target.value)}
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="faceWidthMm" className="font-medium">
                  Face width mm
                </label>
                <InputNumber
                  inputId="faceWidthMm"
                  value={form.faceWidthMm}
                  onValueChange={(e) => setField("faceWidthMm", e.value)}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
              <div className="field col-12 md:col-4">
                <label htmlFor="toleranceMm" className="font-medium">
                  Tolerance mm
                </label>
                <InputNumber
                  inputId="toleranceMm"
                  value={form.toleranceMm}
                  onValueChange={(e) => setField("toleranceMm", e.value)}
                  minFractionDigits={2}
                  maxFractionDigits={3}
                  suffix=" mm"
                  className="w-full"
                />
              </div>
            </div>
          )}
        </Panel>
        <div className="flex flex-wrap align-items-center gap-3">
          <Button
            label={loading ? "Searching MDC..." : "Search MDC"}
            icon="pi pi-search"
            onClick={search}
            loading={loading}
            disabled={loading}
          />
          {loading ? <Message severity="info" text="Searching MDC..." /> : null}
        </div>
      </Card>

      <SearchPayloadPreview payload={payload} />

      {error ? <SearchErrorMessage error={error} /> : null}

      <SearchResultsList response={response} demoProviderWarning={demoProviderWarning} />
    </div>
  );
};

export { buildSearchPayload };

export default ConsumerSearchMockup;
