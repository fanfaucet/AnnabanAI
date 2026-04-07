export default function Panel({ title, children }) {
  return (
    <section className="card">
      <h2 className="font-semibold text-lg mb-3">{title}</h2>
      {children}
    </section>
  );
}
