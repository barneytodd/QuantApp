// format chart legend series
export default function ChartLegend({ series }) {
  return (
    <div className="flex flex-wrap gap-4 items-center">
      {series.map((s) => (
        <div key={s.label} className="flex items-center gap-2">
            
          {/* Colored line */}
          <span
            style={{
              display: "inline-block",
              width: "20px",    // make it long enough to see
              height: "3px",    // thickness of the line
              backgroundColor: s.color,
            }}
          />

          {/* Label */}
          <span className="text-sm font-medium">   {s.label}</span>

          {/* Checkbox for optional toggling */}
          {s.checkbox && (
            <input
              type="checkbox"
              checked={s.checked}
              onChange={s.onChange}
              className="ml-1"
            />
          )}
        </div>
      ))}
    </div>
  );
}