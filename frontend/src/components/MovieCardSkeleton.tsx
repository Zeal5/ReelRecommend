// Skeleton component to show while loading
const MovieCardSkeleton: React.FC<{ size: "sm" | "md" | "lg" }> = ({
  size,
}) => {
  const height = size === "lg" ? "h-72" : size === "md" ? "h-60" : "h-48";
  const width = size === "lg" ? "w-52" : size === "md" ? "w-40" : "w-32";

  return (
    <div className={`flex-shrink-0 ${width} animate-pulse`}>
      <div className={`bg-secondary rounded-lg ${height} w-full`}></div>
      <div className="mt-2 h-4 bg-secondary rounded w-3/4"></div>
      <div className="mt-1 h-3 bg-secondary rounded w-1/2"></div>
    </div>
  );
};

export default MovieCardSkeleton;
