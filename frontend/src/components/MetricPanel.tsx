// AI-ASSISTED: Cursor
// PROMPT: Animated metric bars in glass panel
// ACCEPTED-BY: vignesh

type Props = {
  metrics: Record<string, number>;
};

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric">
      <div className="metric-head">
        <span>{label}</span>
        <span>{Math.round(value)}%</span>
      </div>
      <div className="bar">
        <div className="bar-fill" style={{ width: `${Math.min(100, value)}%` }} />
      </div>
    </div>
  );
}

export function MetricPanel({ metrics }: Props) {
  return (
    <div className="panel panel--glass metrics animate-in animate-in--delay-1">
      <h2>System</h2>
      <div className="metric-bars">
        <Metric label="CPU" value={metrics.cpu_percent} />
        <Metric label="RAM" value={metrics.memory_percent} />
        <Metric label="Disk" value={metrics.disk_percent} />
      </div>
    </div>
  );
}
