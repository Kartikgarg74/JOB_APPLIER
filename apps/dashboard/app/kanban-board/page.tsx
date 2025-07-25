import dynamic from "next/dynamic";

const KanbanBoard = dynamic(() => import("../kanban-board"), { ssr: false, loading: () => <div>Loading Kanban Board...</div> });

export default function KanbanBoardPage() {
  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold mb-6">Job Tracker Kanban Board</h1>
      <KanbanBoard />
    </div>
  );
}
