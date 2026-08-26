export default function RouteStrip({ section }) {
  const [from, to] = section.split(" - ");

  return (
    <div className="mt-4 px-2">
      <div className="flex items-center justify-between text-xs font-medium text-gray-500 mb-1">
        <span>{from}</span>
        <span>{to}</span>
      </div>
      <div className="relative h-1.5 bg-gray-200 rounded-full">
        <div className="absolute inset-0 bg-amber-400 rounded-full opacity-70" />
        <span className="absolute -top-2 left-1/2 -translate-x-1/2 text-sm">🔧</span>
      </div>
    </div>
  );
}