const KnowledgeBlankState = () => {
  return (
    <div className="flex h-32 flex-col items-center justify-center gap-2 rounded-md bg-background-secondary/30 p-4 text-center">
      <p className="text-2xl">📚</p>
      <p className="text-xs text-muted">No knowledge content</p>
      <p className="text-xs text-muted/70">
        Knowledge base is empty
      </p>
    </div>
  )
}

export default KnowledgeBlankState

