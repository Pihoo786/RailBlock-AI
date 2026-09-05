export const DEPARTMENT_FIELDS = {
  engineering: [
    { id: "rail_asset_class", label: "Rail/Asset Class", type: "text" },
    { id: "tgi", label: "TGI", type: "text" },
    { id: "usfd_info", label: "USFD-Related Information", type: "text" },
    { id: "wear_field", label: "Traffic/Wear Field", type: "text" },
  ],
  snt: [
    { id: "asset_type", label: "Asset Type", type: "text" },
    { id: "failure_type", label: "Failure Type", type: "text" },
    { id: "downtime_history", label: "Restoration History / Downtime", type: "text" },
  ],
  trd: [
    { id: "asset_type", label: "Asset Type", type: "text" },
    { id: "wire_condition", label: "Wire Wear/Condition", type: "text" },
    { id: "ohe_fault", label: "OHE Fault Details", type: "text" },
  ],
};