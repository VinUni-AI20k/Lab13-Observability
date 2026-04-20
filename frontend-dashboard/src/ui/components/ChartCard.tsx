import { ReactNode } from "react";

export function ChartCard(props: { title: string; unit: string; hint?: string; children: ReactNode }) {
  return (
    <section className="card">
      <div className="cardHeader">
        <div>
          <div className="cardTitle">{props.title}</div>
          <div className="cardMeta">
            <span className="pill">{props.unit}</span>
            {props.hint ? <span className="hint">{props.hint}</span> : null}
          </div>
        </div>
      </div>
      <div className="cardBody">{props.children}</div>
    </section>
  );
}

