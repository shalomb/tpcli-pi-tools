# tpcli Documentation

Welcome to the tpcli documentation! This documentation is organized using the **Diátaxis framework** for clarity and ease of navigation.

## Documentation Structure

### 📚 [Tutorials](tutorials/) - Learning-Oriented
Step-by-step guides to get started and understand core concepts.

- **[01-getting-started.md](tutorials/01-getting-started.md)** - Installation and first run
- **[02-basic-queries.md](tutorials/02-basic-queries.md)** - Your first API queries
- **[03-authentication-setup.md](tutorials/03-authentication-setup.md)** - Setting up auth properly

### 🎯 [How-To Guides](how-to/) - Task-Oriented
Practical instructions for accomplishing specific tasks.

- **[discover-pi-structure.md](how-to/discover-pi-structure.md)** - Explore PI planning hierarchies by ART/team/release
- **[work-with-user-stories.md](how-to/work-with-user-stories.md)** - CRUD operations on User Stories
- **[manage-assignments.md](how-to/manage-assignments.md)** - Assign users and teams to work items
- **[manage-work-items.md](how-to/manage-work-items.md)** - Update properties, dates, priorities, tags
- **[work-with-collections.md](how-to/work-with-collections.md)** - Access and manage related entities
- **[paginate-results.md](how-to/paginate-results.md)** - Handle large result sets efficiently
- **[api-use-cases.md](how-to/api-use-cases.md)** - Common workflows and patterns
- **[list-and-filter.md](how-to/list-and-filter.md)** - Query, filter, and search entities

### 📖 [Reference](reference/) - Information-Oriented
Lookup documentation for quick answers.

- **[user-story-structure.md](reference/user-story-structure.md)** - User Story fields, relationships, and collections
- **[api-v1-reference.md](reference/api-v1-reference.md)** - REST API v1 complete reference
- **[api-v2-reference.md](reference/api-v2-reference.md)** - REST API v2 (read-only) reference
- **[entity-types.md](reference/entity-types.md)** - All available entity types
- **[query-syntax.md](reference/query-syntax.md)** - Filter expressions and operators
- **[auth-methods.md](reference/auth-methods.md)** - Authentication options and formats
- **[auth-troubleshooting.md](reference/auth-troubleshooting.md)** - Resolving authentication issues

### 💡 [Explanation](explanation/) - Understanding-Oriented
Conceptual information to build understanding.

- **[data-model.md](explanation/data-model.md)** - TargetProcess entity hierarchy
- **[api-architecture.md](explanation/api-architecture.md)** - How the API works
- **[entity-relationships.md](explanation/entity-relationships.md)** - How entities relate

### 🚀 [Ideas & Proposals](ideas/) - Future-Oriented
Feature proposals, enhancement ideas, and design discussions.

- **[entity-discovery-helpers.md](ideas/entity-discovery-helpers.md)** - Instance-agnostic entity lookup helpers
- Browse all [Ideas & Proposals](ideas/)

---

## Quick Navigation

**New to tpcli?**
→ Start with [Tutorials](tutorials/01-getting-started.md)

**Know what you want to do?**
→ Browse [How-To Guides](how-to/)

**Need to look something up?**
→ Check [Reference](reference/)

**Want to understand concepts?**
→ Read [Explanation](explanation/)

**Have an idea or proposal?**
→ See [Ideas & Proposals](ideas/)

---

## Common Tasks

### I want to...

**Understand PI planning structure for my team/ART/release**
→ [discover-pi-structure.md](how-to/discover-pi-structure.md)

**Get started with tpcli**
→ [01-getting-started.md](tutorials/01-getting-started.md)

**Work with User Stories (create, read, update, delete)**
→ [work-with-user-stories.md](how-to/work-with-user-stories.md)

**Access collections (bugs, tasks, comments, times)**
→ [work-with-collections.md](how-to/work-with-collections.md)

**Understand User Story structure and fields**
→ [user-story-structure.md](reference/user-story-structure.md)

**List all user stories with filtering**
→ [list-and-filter.md](how-to/list-and-filter.md)

**Handle pagination for large results**
→ [paginate-results.md](how-to/paginate-results.md)

**Find items created in the last week**
→ [list-and-filter.md#date-filters](how-to/list-and-filter.md)

**Include related project information**
→ [work-with-nested-entities.md](how-to/work-with-nested-entities.md)

**Understand the TargetProcess data structure**
→ [data-model.md](explanation/data-model.md)

**Set up API authentication**
→ [03-authentication-setup.md](tutorials/03-authentication-setup.md)

**Troubleshoot authentication issues**
→ [auth-troubleshooting.md](reference/auth-troubleshooting.md)

**Assign users/teams to work items**
→ [manage-assignments.md](how-to/manage-assignments.md)

**Update dates, priorities, tags, effort**
→ [manage-work-items.md](how-to/manage-work-items.md)

**Follow common API patterns and workflows**
→ [api-use-cases.md](how-to/api-use-cases.md)

**See all available filters**
→ [query-syntax.md](reference/query-syntax.md)

**Get details about an entity type**
→ [entity-types.md](reference/entity-types.md)

---

## Documentation Format

Each guide follows a consistent format:

- **Tutorials**: Follow a step-by-step learning path
- **How-To**: Task-focused with examples and explanations
- **Reference**: Organized for easy lookup, alphabetical or logical
- **Explanation**: Conceptual, building understanding

---

## Versions

- **tpcli**: 0.1.0 (MVP)
- **TargetProcess API**: v1 & v2
- **Last Updated**: November 29, 2025

---

## Related Resources

- **Project README**: `~/shalomb/tpcli/README.md`
- **Project Summary**: `~/shalomb/tpcli/PROJECT-SUMMARY.md`
- **TargetProcess API Docs**: https://dev.targetprocess.com/docs
- **Diátaxis Framework**: https://diataxis.fr/

---

**Start reading**: [Getting Started Tutorial →](tutorials/01-getting-started.md)
