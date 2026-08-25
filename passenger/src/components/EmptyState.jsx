export default function EmptyState({ query }) {
  return (
    <p className="text-center text-gray-500 text-sm mt-10">
      No scheduled disruptions found for train {query}.
    </p>
  );
}