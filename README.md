# FM27 Filters and Views

Moneyball recruitment pack for Football Manager 27.

- **54 filters:** 18 recruitment profiles, each with Early, Midseason and Full Season versions.
- **36 matching views:** Player Search and Shortlist versions for every profile.
- **League-free masters:** choose recruitment markets for the team you manage.

Start with the [step-by-step installation guide](docs/installation.md) and [adapting the pack to your league](docs/league-selection.md).

## Install

Copy the `.fmf` files from the supplied `player search filters` and `views` folders into the matching folders under your Football Manager 27 user directory. Create the folders if needed. In the repository download, these two folders are inside `pack`; in the dedicated pack ZIP, they are at the top level.

Typical Windows location: `Documents/Sports Interactive/Football Manager 27/`.

In FM27:

1. Open Recruitment > Player Database > Edit Search.
2. Use the gear menu > Load Filter and choose a role profile.
3. Apply the search, then use the view dropdown > Import View to load that profile's **Search** view.
4. On a shortlist, import its **Shortlist** view instead.

A ZIP with the two installation folders is available in [downloads](downloads/FM27-Filters-and-Views-v0.2.zip).

## Season versions

| Version | Minimum minutes |
|---|---:|
| Early | No minutes condition |
| Midseason | 1,000 |
| Full Season | 2,000 |

Performance thresholds stay the same across versions. Check the Minutes column when using Early: a few appearances can produce misleading rates. Presets do not adjust to the game date or to individual leagues' calendars.

## Recruitment profiles

Goalkeeper; defensive and ball-playing centre-back; defensive full-back; attacking wing-back; inverted full-back; holding midfielder; deep playmaker; ball winner; box-to-box midfielder; attacking midfielder; free-role attacking midfielder; touchline winger; inside forward; goalscorer; target forward; linking forward; pressing forward.

Flank profiles include both sides. Narrow the position in Edit Search when recruiting for one vacancy. Both tactical-role dropdowns stay Any; statistics define the recruitment profile.

See [every threshold and its source](docs/profiles.md). Most thresholds are provisional choices for this pack. Screenshot-derived references are identified. These profiles do not cover every named tactical role in FM27.

## Keep markets separate

Load a role first, then add your own league/nation, affordability, age and interest settings. Save a club-specific working copy and preserve the master.

Use OR within the eligible-leagues group and AND between that group and the role/statistical conditions. Check the grouping in FM. Loading a second preset has not been shown to merge conditions. See [market guidance](docs/league-selection.md).

## Verification

Built against Steam build **26340721**. Generated archives, column identifiers, integer boundaries and all 213 threshold values passed structural checks. No master filter contains a league restriction.

User screenshots confirmed the original right-wing-back Season/Midseason settings and the corrected ball-playing centre-back Early filter with its populated Search view. Other profiles and views have not all been checked in-game. Search-result counts and successful imports do not establish recruitment quality or persistence after saving/reloading.

See [validation notes](docs/validation.md), [stat-filter availability](docs/filter-availability.csv) and [sources](docs/sources.md).

## Build tools

Prebuilt files can be installed without Python. The tools require Python 3.14 and `requirements.txt`. Rebuilding also requires local native exports and extracted metadata that are excluded from the repository. See [developer notes](docs/development.md).

No game binaries, extracted game assets, private sample exports, save files, credentials or local installation logs are included.
