export default function AboutPage() {
  return (
    <div className="max-w-md">
      <h1 className="text-xl font-semibold text-gray-800">About RailBlock</h1>
      <p className="text-sm text-gray-600 mt-3 leading-relaxed">
        RailBlock is a passenger-facing interface for an AI-powered railway
        maintenance block planning system. When engineers need to schedule
        track or equipment maintenance, the system finds the time window that
        causes the least disruption to train schedules. Once a railway
        official approves a block, affected passengers can check this page
        for the train, section, timing, and reason — without exposing any
        internal planning data.
      </p>
    </div>
  );
}