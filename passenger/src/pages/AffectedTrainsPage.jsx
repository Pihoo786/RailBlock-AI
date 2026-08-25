import StatusCard from "../components/StatusCard";
import { mockBlocks } from "../data/mockBlocks";

export default function AffectedTrainsPage() {
  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">Currently Affected Trains</h1>
      <p className="text-sm text-gray-500 mt-1">
        Trains with an approved or scheduled maintenance block today.
      </p>
      {mockBlocks.map((block) => (
        <StatusCard key={block.train_number} block={block} />
      ))}
    </div>
  );
}