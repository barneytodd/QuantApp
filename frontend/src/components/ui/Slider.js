export default function Slider({ label, value, min, max, step = 1, onChange }) {
  return (
    <div>
      <label className="text-sm">{label}</label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full"
      />
      <span className="ml-2">{value}</span>
    </div>
  );
}
