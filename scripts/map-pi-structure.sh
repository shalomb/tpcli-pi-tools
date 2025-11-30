#!/bin/bash

# Map TargetProcess PI Structure
# Usage: ./map-pi-structure.sh --art "Data, Analytics and Digital"
#    or: ./map-pi-structure.sh --team "Example Team"
#    or: ./map-pi-structure.sh --release "PI-4/25"

set -e

TPCLI="${TPCLI:-.}/tpcli"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --art)
      ART_NAME="$2"
      shift 2
      ;;
    --team)
      TEAM_NAME="$2"
      shift 2
      ;;
    --release)
      RELEASE_NAME="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: $0 [--art NAME | --team NAME | --release NAME]"
      exit 1
      ;;
  esac
done

if [ -z "$ART_NAME" ] && [ -z "$TEAM_NAME" ] && [ -z "$RELEASE_NAME" ]; then
  echo "Error: Must provide --art, --team, or --release"
  exit 1
fi

# Helper function to extract JSON from tpcli output (skips Request/Response lines)
extract_json() {
  awk '/^[{\[]/{flag=1} flag'
}

# Helper function to find ID by name
find_id_by_field() {
  local entity=$1
  local field=$2
  local name=$3

  $TPCLI list "$entity" --take 1000 2>&1 | extract_json | jq -r ".[] | select(.${field} == \"${name}\") | .Id" 2>/dev/null | head -1
}

# Find ART ID if name provided
if [ -n "$ART_NAME" ]; then
  echo -e "${BLUE}🔍 Finding ART: ${YELLOW}${ART_NAME}${NC}"
  ART_ID=$(find_id_by_field "AgileReleaseTrains" "Name" "$ART_NAME")
  if [ -z "$ART_ID" ]; then
    echo "Error: ART '$ART_NAME' not found"
    exit 1
  fi
  echo -e "${GREEN}✓ Found ART ID: ${CYAN}${ART_ID}${NC}\n"
fi

# Find Team ID if name provided
if [ -n "$TEAM_NAME" ]; then
  echo -e "${BLUE}🔍 Finding Team: ${YELLOW}${TEAM_NAME}${NC}"
  TEAM_ID=$(find_id_by_field "Teams" "Name" "$TEAM_NAME")
  if [ -z "$TEAM_ID" ]; then
    echo "Error: Team '$TEAM_NAME' not found"
    exit 1
  fi
  echo -e "${GREEN}✓ Found Team ID: ${CYAN}${TEAM_ID}${NC}\n"
fi

# Find Release ID if name provided
if [ -n "$RELEASE_NAME" ]; then
  echo -e "${BLUE}🔍 Finding Release: ${YELLOW}${RELEASE_NAME}${NC}"
  RELEASE_ID=$(find_id_by_field "Releases" "Name" "$RELEASE_NAME")
  if [ -z "$RELEASE_ID" ]; then
    echo "Error: Release '$RELEASE_NAME' not found"
    exit 1
  fi
  echo -e "${GREEN}✓ Found Release ID: ${CYAN}${RELEASE_ID}${NC}\n"
fi

# Build the hierarchy
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}PI STRUCTURE MAP${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"

# If we have an ART, show its structure
if [ -n "$ART_ID" ]; then
  echo -e "${CYAN}📦 AGILE RELEASE TRAIN${NC}"
  ART_INFO=$($TPCLI get AgileReleaseTrains "$ART_ID" 2>&1 | extract_json)
  ART_DISPLAY_NAME=$(echo "$ART_INFO" | jq -r '.Name')
  echo -e "  ${GREEN}✓${NC} ${ART_DISPLAY_NAME} (ID: ${ART_ID})\n"

  # Find all releases for this ART
  echo -e "${CYAN}📋 RELEASES/PROGRAM INCREMENTS${NC}"
  RELEASES=$($TPCLI list Releases --where "AgileReleaseTrain.Id eq $ART_ID" --take 100 2>&1 | extract_json)
  RELEASE_COUNT=$(echo "$RELEASES" | jq 'length')

  for i in $(seq 0 $((RELEASE_COUNT - 1))); do
    RELEASE=$(echo "$RELEASES" | jq ".[$i]")
    RELEASE_ID=$(echo "$RELEASE" | jq -r '.Id')
    RELEASE_NAME=$(echo "$RELEASE" | jq -r '.Name')
    RELEASE_STATUS=$(echo "$RELEASE" | jq -r '.IsCurrent')
    IS_CURRENT=""
    if [ "$RELEASE_STATUS" = "true" ]; then
      IS_CURRENT=" ${YELLOW}[CURRENT]${NC}"
    fi
    echo -e "  ${GREEN}├─${NC} ${RELEASE_NAME}${IS_CURRENT} (ID: ${RELEASE_ID})"

    # Find Program PI Objectives for this release
    PROG_OBJS=$($TPCLI list ProgramPIObjectives --where "Release.Id eq $RELEASE_ID" --take 100 2>&1 | extract_json)
    PROG_OBJ_COUNT=$(echo "$PROG_OBJS" | jq 'length')

    if [ "$PROG_OBJ_COUNT" -gt 0 ]; then
      echo -e "  ${GREEN}│  ${CYAN}🎯 PROGRAM PI OBJECTIVES${NC}"
      for j in $(seq 0 $((PROG_OBJ_COUNT - 1))); do
        PROG_OBJ=$(echo "$PROG_OBJS" | jq ".[$j]")
        PROG_OBJ_ID=$(echo "$PROG_OBJ" | jq -r '.Id')
        PROG_OBJ_NAME=$(echo "$PROG_OBJ" | jq -r '.Name')
        PROG_OBJ_STATUS=$(echo "$PROG_OBJ" | jq -r '.EntityState.Name')
        echo -e "  ${GREEN}│  ├─${NC} ${PROG_OBJ_NAME} [${PROG_OBJ_STATUS}] (ID: ${PROG_OBJ_ID})"
      done
    fi

    # Find teams and their objectives for this release
    TEAM_OBJS=$($TPCLI list TeamPIObjectives --where "Release.Id eq $RELEASE_ID" --take 100 2>&1 | extract_json)
    TEAM_OBJ_COUNT=$(echo "$TEAM_OBJS" | jq 'length')

    if [ "$TEAM_OBJ_COUNT" -gt 0 ]; then
      echo -e "  ${GREEN}│  ${CYAN}👥 TEAM PI OBJECTIVES${NC}"
      for j in $(seq 0 $((TEAM_OBJ_COUNT - 1))); do
        TEAM_OBJ=$(echo "$TEAM_OBJS" | jq ".[$j]")
        TEAM_OBJ_ID=$(echo "$TEAM_OBJ" | jq -r '.Id')
        TEAM_OBJ_NAME=$(echo "$TEAM_OBJ" | jq -r '.Name')
        TEAM_OBJ_STATUS=$(echo "$TEAM_OBJ" | jq -r '.EntityState.Name')
        TEAM_NAME_OBJ=$(echo "$TEAM_OBJ" | jq -r '.Team.Name // "Unknown"')
        IS_LAST="false"
        if [ "$j" -eq $((TEAM_OBJ_COUNT - 1)) ]; then
          IS_LAST="true"
        fi

        if [ "$IS_LAST" = "true" ]; then
          echo -e "  ${GREEN}│  └─${NC} ${TEAM_NAME_OBJ}: ${TEAM_OBJ_NAME} [${TEAM_OBJ_STATUS}] (ID: ${TEAM_OBJ_ID})"
        else
          echo -e "  ${GREEN}│  ├─${NC} ${TEAM_NAME_OBJ}: ${TEAM_OBJ_NAME} [${TEAM_OBJ_STATUS}] (ID: ${TEAM_OBJ_ID})"
        fi
      done
    fi

    if [ "$i" -lt $((RELEASE_COUNT - 1)) ]; then
      echo -e "  ${GREEN}│${NC}"
    fi
  done
  echo ""
fi

# If we have a Team, show its structure
if [ -n "$TEAM_ID" ]; then
  echo -e "${CYAN}👥 TEAM${NC}"
  TEAM_INFO=$($TPCLI get Teams "$TEAM_ID" 2>&1 | extract_json)
  TEAM_DISPLAY_NAME=$(echo "$TEAM_INFO" | jq -r '.Name')
  echo -e "  ${GREEN}✓${NC} ${TEAM_DISPLAY_NAME} (ID: ${TEAM_ID})\n"

  # Find all PI Objectives for this team
  echo -e "${CYAN}🎯 PI OBJECTIVES${NC}"
  TEAM_PI_OBJS=$($TPCLI list TeamPIObjectives --where "Team.Id eq $TEAM_ID" --take 100 2>&1 | extract_json)
  TEAM_PI_OBJ_COUNT=$(echo "$TEAM_PI_OBJS" | jq 'length')

  if [ "$TEAM_PI_OBJ_COUNT" -eq 0 ]; then
    echo -e "  ${YELLOW}○${NC} No PI Objectives found"
  else
    for i in $(seq 0 $((TEAM_PI_OBJ_COUNT - 1))); do
      TEAM_PI_OBJ=$(echo "$TEAM_PI_OBJS" | jq ".[$i]")
      OBJ_ID=$(echo "$TEAM_PI_OBJ" | jq -r '.Id')
      OBJ_NAME=$(echo "$TEAM_PI_OBJ" | jq -r '.Name')
      OBJ_STATUS=$(echo "$TEAM_PI_OBJ" | jq -r '.EntityState.Name')
      RELEASE_NAME=$(echo "$TEAM_PI_OBJ" | jq -r '.Release.Name // "No Release"')

      echo -e "  ${GREEN}├─${NC} ${OBJ_NAME} [${OBJ_STATUS}] (ID: ${OBJ_ID})"
      echo -e "  ${GREEN}│  ${CYAN}Release:${NC} ${RELEASE_NAME}"

      # Find features related to this objective
      FEATURES=$($TPCLI list Features --where "TeamPIObjective.Id eq $OBJ_ID" --take 100 2>&1 | extract_json)
      FEATURE_COUNT=$(echo "$FEATURES" | jq 'length' 2>/dev/null || echo "0")

      if [ -n "$FEATURE_COUNT" ] && [ "$FEATURE_COUNT" -gt 0 ]; then
        echo -e "  ${GREEN}│  ${CYAN}Features:${NC}"
        for f in $(seq 0 $((FEATURE_COUNT - 1))); do
          FEATURE=$(echo "$FEATURES" | jq ".[$f]")
          FEATURE_ID=$(echo "$FEATURE" | jq -r '.Id')
          FEATURE_NAME=$(echo "$FEATURE" | jq -r '.Name')
          FEATURE_STATUS=$(echo "$FEATURE" | jq -r '.EntityState.Name')

          if [ "$f" -lt $((FEATURE_COUNT - 1)) ]; then
            echo -e "  ${GREEN}│  ├─${NC} ${FEATURE_NAME} [${FEATURE_STATUS}] (ID: ${FEATURE_ID})"
          else
            echo -e "  ${GREEN}│  └─${NC} ${FEATURE_NAME} [${FEATURE_STATUS}] (ID: ${FEATURE_ID})"
          fi
        done
      fi

      if [ "$i" -lt $((TEAM_PI_OBJ_COUNT - 1)) ]; then
        echo -e "  ${GREEN}│${NC}"
      fi
    done
  fi
  echo ""
fi

# If we have a Release, show its structure
if [ -n "$RELEASE_ID" ]; then
  echo -e "${CYAN}📋 RELEASE/PROGRAM INCREMENT${NC}"
  RELEASE_INFO=$($TPCLI get Releases "$RELEASE_ID" 2>&1 | extract_json)
  RELEASE_DISPLAY_NAME=$(echo "$RELEASE_INFO" | jq -r '.Name')
  ART_INFO=$(echo "$RELEASE_INFO" | jq -r '.AgileReleaseTrain.Name // "N/A"')
  echo -e "  ${GREEN}✓${NC} ${RELEASE_DISPLAY_NAME} (ID: ${RELEASE_ID})"
  echo -e "  ${GREEN}  ART:${NC} ${ART_INFO}\n"

  # Find all objectives for this release
  echo -e "${CYAN}🎯 PROGRAM PI OBJECTIVES${NC}"
  PROG_OBJS=$($TPCLI list ProgramPIObjectives --where "Release.Id eq $RELEASE_ID" --take 100 2>&1 | extract_json)
  PROG_OBJ_COUNT=$(echo "$PROG_OBJS" | jq 'length')

  if [ "$PROG_OBJ_COUNT" -eq 0 ]; then
    echo -e "  ${YELLOW}○${NC} No Program PI Objectives found"
  else
    for i in $(seq 0 $((PROG_OBJ_COUNT - 1))); do
      PROG_OBJ=$(echo "$PROG_OBJS" | jq ".[$i]")
      OBJ_ID=$(echo "$PROG_OBJ" | jq -r '.Id')
      OBJ_NAME=$(echo "$PROG_OBJ" | jq -r '.Name')
      OBJ_STATUS=$(echo "$PROG_OBJ" | jq -r '.EntityState.Name')

      echo -e "  ${GREEN}├─${NC} ${OBJ_NAME} [${OBJ_STATUS}] (ID: ${OBJ_ID})"
    done
  fi

  echo -e "\n${CYAN}👥 TEAM PI OBJECTIVES${NC}"
  TEAM_OBJS=$($TPCLI list TeamPIObjectives --where "Release.Id eq $RELEASE_ID" --take 100 2>&1 | extract_json)
  TEAM_OBJ_COUNT=$(echo "$TEAM_OBJS" | jq 'length')

  if [ "$TEAM_OBJ_COUNT" -eq 0 ]; then
    echo -e "  ${YELLOW}○${NC} No Team PI Objectives found"
  else
    for i in $(seq 0 $((TEAM_OBJ_COUNT - 1))); do
      TEAM_OBJ=$(echo "$TEAM_OBJS" | jq ".[$i]")
      OBJ_ID=$(echo "$TEAM_OBJ" | jq -r '.Id')
      OBJ_NAME=$(echo "$TEAM_OBJ" | jq -r '.Name')
      OBJ_STATUS=$(echo "$TEAM_OBJ" | jq -r '.EntityState.Name')
      TEAM_NAME=$(echo "$TEAM_OBJ" | jq -r '.Team.Name // "Unknown"')

      echo -e "  ${GREEN}├─${NC} ${TEAM_NAME}: ${OBJ_NAME} [${OBJ_STATUS}] (ID: ${OBJ_ID})"
    done
  fi
  echo ""
fi

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
