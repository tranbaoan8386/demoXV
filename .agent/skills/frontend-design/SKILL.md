---
name: frontend-design
description: Design and implement production-quality DemoXV React interfaces with product-specific visual direction, consistent UI patterns, responsive behavior, accessibility, and clear interaction states. Use when creating a new page or major component, redesigning an existing screen, improving UI/UX, or implementing forms, upload flows, dashboards, tables, lists, settings, or admin interfaces.
compatibility: React, Vite, TypeScript and Tailwind CSS projects; intended for DemoXV frontend work.
metadata:
  scope: demoxv-frontend
  version: "2.0"
---

# Frontend Design

Use this skill as a **task workflow**, not as a replacement for project instructions.

## Read first

Before implementation, read only what is relevant:

1. `.github/instructions/frontend.instructions.md`
2. `.agent/rules/frontend-ui.md`
3. the target feature and adjacent frontend code
4. existing reusable components and tokens
5. `references/` files only when the current task needs their detail

## Workflow

### 1. Understand

Inspect the current implementation before designing.

Identify:

- user and primary job
- existing page shell/navigation
- established components
- spacing, typography, color and surface patterns
- data and interaction states
- responsive constraints

Do not invent a new visual language when an established pattern already solves the problem.

### 2. Define the design direction

For a new or substantially changed screen, briefly decide:

- **purpose** — what the user is trying to accomplish
- **hierarchy** — what must be seen first, second and third
- **composition** — primary and secondary regions
- **signature** — one product/domain-specific element that makes the screen feel intentional
- **rejected defaults** — generic UI patterns that would be easy to generate but are wrong for the task

Use the product domain to drive the composition. Prefer a task-oriented workspace over a generic dashboard template when the task is document- or workflow-centric.

### 3. Plan states

List the relevant states before coding:

- default
- hover/focus/active
- loading
- empty
- error
- success
- disabled
- long content
- mobile

Do not optimize only for the happy-path screenshot.

### 4. Implement

Implement with the existing:

- React patterns
- TypeScript types
- Tailwind utilities/tokens
- component library or primitives
- hooks/services/API boundaries

Prefer the smallest component structure that keeps responsibilities clear.

Do not add dependencies or abstractions without a concrete need.

### 5. Review visually

Before finishing, check:

- **Hierarchy:** Is the primary task obvious?
- **Specificity:** Does the screen feel like DemoXV rather than a generic AI template?
- **Consistency:** Does it belong beside adjacent screens?
- **States:** Are important interaction states represented?
- **Responsive:** Does the composition adapt rather than merely shrink?
- **Accessibility:** Are semantics, labels, focus, contrast and status communication adequate?

### 6. Validate

Run the smallest relevant checks available in the repository and report only what was actually verified.

## Decision rules

When choices conflict, prioritize in this order:

1. correctness and existing architecture
2. user task clarity
3. consistency with existing product patterns
4. accessibility and responsive behavior
5. visual polish
6. decorative effects

## References

Use the bundled references when the task needs deeper guidance:

- `references/ui-heuristics.md` — visual decision heuristics
- `references/validation-checklist.md` — completion checklist

Keep this `SKILL.md` procedural and use references for detail so the skill stays easy to activate and maintain.
