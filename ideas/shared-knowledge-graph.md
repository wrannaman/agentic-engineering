# Shared Knowledge Graph: From Local Memory to Team Brain

*Status: exploration. Not built. Not scoped. Worth thinking about for a while before committing.*

## The shift

The KB server today is a flat document store. Each developer's Claude also keeps a local, file-based memory (`~/.claude/projects/*/memory/`) — personal preferences, feedback, project context. That memory is **local**: it lives on one laptop, belongs to one person, and compounds one head at a time.

The interesting move is **local → global**: promote personal learnings into a shared structure the whole team's agents can query, so one developer's "I figured out that X breaks when Y" becomes every agent's default knowledge within hours, not quarters.

Flat docs can carry the text of a learning. A graph can carry the *relationships* — and relationships are where compounding actually happens.

## Why a graph (and why Apache AGE)

The payoff isn't storage — it's traversal queries that are painful in SQL and impossible in flat files:

- `skill --depends-on--> skill` — what breaks if we change the review skill?
- `learning --applies-to--> domain` — what has the team learned about auth?
- `PR --teaches--> pattern --used-in--> service` — where else is this pattern?
- `developer --discovered--> learning --compounds-with--> learning` — which learnings stack?
- Multi-hop: "show me every pattern downstream of the compound loop that's been validated in a merged PR in the last 90 days."

Apache AGE gives us Cypher on top of Postgres. Concretely:

- **One database, two query languages.** Documents, users, PR metadata stay in normal tables. The graph lives as an AGE extension in the same Postgres. No second system to operate.
- **We already run Postgres.** The KB server supports tsvector. Adding AGE is `CREATE EXTENSION`, not a new service.
- **Cypher is genuinely better for traversal.** `MATCH (s:Skill)-[:DEPENDS_ON*1..3]->(t:Skill)` vs. a recursive CTE — the first is readable, the second is a code review landmine.

## Why *not* a graph

Don't over-index on elegance:

- **Operational cost is real.** AGE is less battle-tested than core Postgres. Extensions add upgrade risk, monitoring surface, and "nobody on the team knows Cypher" friction.
- **Most questions aren't multi-hop.** "Find docs about auth" is keyword search. "Find learnings tagged with `auth` from the last month" is a WHERE clause. You don't need a graph for either.
- **pgvector + a typed `edges` table gets you 80%.** A single `(from_id, to_id, kind, metadata)` table plus indexes handles 1-hop and 2-hop queries fine. You hit the graph-DB wall at 3+ hops or when the query planner on recursive CTEs gives up — which is a real moment, but it's a moment you should *wait for*, not design around preemptively.

**Rule of thumb:** stay on plain Postgres + pgvector + edges table until you have a concrete traversal query you've tried to write in SQL and hated. Then adopt AGE, migrating only the traversal-heavy entities.

## The harder problem: the write path

The DB is the boring decision. The real design question is:

**Who — or what — promotes a personal memory to the shared graph?**

Some failure modes if we get this wrong:

- **Silent noise.** Every developer's typos, one-off preferences, and stale fixes end up in the team brain. Signal-to-noise collapses. Agents get worse, not better.
- **Silent conflicts.** Dev A saves "always use X." Dev B saves "never use X." Both are right in their own context. The graph now poisons every agent that touches either.
- **Promotion theatre.** We build a "promote to team" button nobody clicks, and the graph stays empty.
- **Over-promotion.** Auto-promote everything, and the team brain becomes unreadable within a week.

Sketches worth exploring (none decided):

1. **PR-gated promotion.** A memory is only promoted when the code that motivated it lands in a merged PR. The PR becomes the provenance edge: `learning --derived-from--> PR`. Auto-expires if the PR is reverted.
2. **Quorum / reinforcement.** A learning promotes when N distinct developers' agents independently save a similar memory. The graph tracks convergence, not individual opinion.
3. **Curator-in-the-loop.** One person on the team runs a weekly `/compound` pass over promoted candidates. Low ceremony, human judgment, scales badly past ~20 people.
4. **Decay by default.** Every edge has a TTL. Learnings that aren't reinforced (by new PRs, new hits, new agreement) fade. The graph stays current without manual pruning.

My current bias: **(1) + (4)** — PR-gated promotion with decay — is the lowest-ceremony version that doesn't collapse under noise. The PR is the team's existing quality gate; reusing it for knowledge promotion means we don't invent a new process.

## What would convince us to actually build this

Not "it sounds cool." These:

- A specific traversal query we've wanted to run 3+ times and couldn't (e.g., "what patterns from the last 10 reviews apply to this PR?").
- Evidence that the local-memory compound loop is saturating — individual agents are getting better, but the team isn't.
- A second team adopting the agentic-eng stack who'd benefit from cross-team knowledge transfer.

Until then: keep the KB flat, keep memories local, and keep thinking.

## Open questions

- Does the graph replace the flat KB, or sit alongside it? (Probably alongside — different access patterns.)
- How do we represent *disagreement* in the graph? (A single edge can't capture "Dev A thinks X, Dev B thinks not-X, both have context.")
- Do agents write to the graph directly, or only through an MCP tool with validation?
- What's the read path latency budget? Cypher traversal over a large graph isn't free.
