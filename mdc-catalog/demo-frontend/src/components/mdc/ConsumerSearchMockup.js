import React, { useEffect, useMemo, useRef, useState } from "react";
import { Button } from "primereact/button";
import { Card } from "primereact/card";
import { Dropdown } from "primereact/dropdown";
import { InputNumber } from "primereact/inputnumber";
import { InputText } from "primereact/inputtext";
import { Message } from "primereact/message";
import { MultiSelect } from "primereact/multiselect";
import { Panel } from "primereact/panel";
import { Toast } from "primereact/toast";
import { getCatalogFilters, normalizeCatalogFilters } from "@/services/mdc/catalog.service";
import { searchServiceDiscovery } from "@/services/mdc/search.service";
import SearchErrorMessage from "./SearchErrorMessage";
import SearchPayloadPreview from "./SearchPayloadPreview";
import SearchResultsList from "./SearchResultsList";

const emptyCatalog = {
  partFamilies: [], partTypes: {}, materials: [], processes: [],
  certifications: [], serviceCategoryByFamily: {},
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
  const { partType } = form;
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

const buildSearchPayload = (form, categoryMap = {}) => {
  const { partFamily, partType } = form;
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
    service_category: categoryMap[partFamily],
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
  const [catalogFilters, setCatalogFilters] = useState(emptyCatalog);
  const [filterSource, setFilterSource] = useState("loading");
  const [form, setForm] = useState({
    consumerId: "consumer_demo_001",
    requestId: `req-demo-${Date.now()}`,
    partFamily: "gear",
    partType: "spur_gear",
    material: "",
    processes: [],
    certification: "",
    requirement: "",
    module: null,
    diametralPitch: null,
    outsideDiameterMm: null,
    gearQuality: "",
    faceWidthMm: null,
    lengthMm: null,
    outerDiameterMm: null,
    splineModule: null,
    internalDiameterMm: null,
    wallThicknessMm: null,
    metalLengthMm: null,
    metalWidthMm: null,
    metalHeightMm: null,
    metalThicknessMm: null,
    metalDiameterMm: null,
    metalInnerDiameterMm: null,
    metalOuterDiameterMm: null,
    metalWallThicknessMm: null,
    metalWeightKg: null,
    flangeLengthMm: null,
    horizontalFlangeLengthMm: null,
    flangeDiameterMm: null,
    mountingHolesCount: null,
    holeDiameterMm: null,
    shaftOrBoreDiameterMm: null,
    boreDiameterMm: null,
    materialGrade: "",
    surfaceFinish: "",
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
    toleranceMm: null,
  });

  const normalizedPartFamily = form.partFamily;
  const isMetalPart = normalizedPartFamily === "metal_part";
  const availablePartTypes = catalogFilters.partTypes[normalizedPartFamily] || [];
  const payload = useMemo(
    () => buildSearchPayload(form, catalogFilters.serviceCategoryByFamily),
    [form, catalogFilters.serviceCategoryByFamily]
  );

  useEffect(() => {
    let active = true;

    getCatalogFilters()
      .then((data) => {
        if (!active) return;
        setCatalogFilters(normalizeCatalogFilters(data));
        setFilterSource("canonical");
      })
      .catch(() => {
        if (!active) return;
        setCatalogFilters(emptyCatalog);
        setFilterSource("unavailable");
      });

    return () => {
      active = false;
    };
  }, []);

  const setField = (field, value) =>
    setForm((current) => ({ ...current, [field]: value }));

  const handlePartFamilyChange = (value) => {
    const family = value;
    const nextPartType = catalogFilters.partTypes[family]?.[0]?.value;

    setForm((current) => ({
      ...current,
      partFamily: family,
      partType: nextPartType,
    }));
  };

  const search = async () => {
    setError(null);
    setResponse(null);
    setLoading(true);

    try {
      const result = await searchServiceDiscovery(payload);
      if (result?.contract_version !== "1.0" || !Array.isArray(result.results)
        || !Number.isInteger(result.result_count)) {
        throw new Error("The MDC search response does not match contract version 1.0.");
      }
      setResponse(result);
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
        {filterSource === "unavailable" ? (
          <Message
            severity="warn"
            text="Current catalogue filters are unavailable. Search requires the live vocabulary."
            className="w-full justify-content-start mb-3"
          />
        ) : null}
        {filterSource === "loading" ? (
          <Message
            severity="info"
            text="Loading current catalogue filters..."
            className="w-full justify-content-start mb-3"
          />
        ) : null}
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
              options={catalogFilters.partFamilies}
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
              optionLabel="label"
              optionValue="value"
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
              options={catalogFilters.materials}
              onChange={(e) => setField("material", e.value)}
              optionLabel="label"
              optionValue="value"
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
              options={catalogFilters.processes}
              onChange={(e) => setField("processes", e.value)}
              optionLabel="label"
              optionValue="value"
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
              options={catalogFilters.certifications}
              onChange={(e) => setField("certification", e.value)}
              optionLabel="label"
              optionValue="value"
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
            disabled={loading || filterSource !== "canonical" || !payload.service_category
              || !availablePartTypes.some((item) => item.value === form.partType)}
          />
          {loading ? <Message severity="info" text="Searching MDC..." /> : null}
        </div>
      </Card>

      <SearchPayloadPreview payload={payload} />

      {error ? <SearchErrorMessage error={error} /> : null}

      <SearchResultsList response={response} />
    </div>
  );
};

export { buildSearchPayload };

export default ConsumerSearchMockup;
