export const mockTrainResponse = {
  "12627": {
    train_number: "12627",
    blocks: [
      {
        section: "Chennai - Katpadi",
        start_time: "2026-08-26T10:00:00",
        end_time: "2026-08-26T12:00:00",
        expected_delay_minutes: 25,
        reason: "Track maintenance",
        status: "SCHEDULED",
      },
    ],
  },
  "12639": {
    train_number: "12639",
    blocks: [],
  },
};

export const mockAllBlocks = [
  {
    train_number: "12627",
    section: "Chennai - Katpadi",
    start_time: "2026-08-26T10:00:00",
    end_time: "2026-08-26T12:00:00",
    expected_delay_minutes: 25,
    reason: "Track maintenance",
    status: "SCHEDULED",
  },
];