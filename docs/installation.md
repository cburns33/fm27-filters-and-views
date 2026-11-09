# Install the filters and views

## Download

1. Open the repository's [download ZIP](../downloads/FM27-Filters-and-Views-v0.2.zip).
2. Use GitHub's download button to save the ZIP, then extract it.
3. Inside are two folders: `player search filters` and `views`.

You can also use Code > Download ZIP on the repository homepage. With that download, the installation folders are inside `pack`.

## Copy into FM27 on Windows

Find your Football Manager 27 **user-data folder**, normally:

```text
Documents\Sports Interactive\Football Manager 27\
```

Use the folder containing your saves, graphics and other custom files. If Documents is redirected to another drive or OneDrive, use that location. If you configured a custom FM user-data location, use it.

Copy the `.fmf` files so the final structure looks like this:

```text
Football Manager 27\
  player search filters\
    CB Ball Playing - Early.fmf
    CB Ball Playing - Midseason.fmf
    ...
  views\
    CB Ball Playing - Search.fmf
    CB Ball Playing - Shortlist.fmf
    ...
```

Create either folder if it is missing. Copy the files **inside** the supplied folders to avoid an extra nested folder level.

## Load a filter

1. In your save, open Recruitment > Player Database > Edit Search.
2. Open the gear menu and choose Load Filter.
3. Select a role profile and season version, then apply the search.

| Version | Minimum minutes | How to use it |
|---|---:|---|
| Early | No minutes condition | Check minutes before trusting a high per-90 rate. |
| Midseason | 1,000 | Useful once candidates have accumulated this much playing time. |
| Full Season | 2,000 | A larger sample when the relevant competition is far enough into its season. |

These are manual choices. FM does not switch them for you, and the files do not detect which month each league is in.

## Load the matching view

On the player-results table, open the view dropdown, choose Import View, and select the profile's **Search** view. On a shortlist, import the **Shortlist** version instead.

The same view works with all three season versions. It displays minutes near the front, the filter's core statistics, and supporting measures. Scroll sideways or adjust column widths if your display cannot fit every column. Views do not enforce a sort order; the [profile guide](profiles.md) suggests where to start comparing.

## Set it up for your club

Every master is league-free. After loading a role, add your recruitment markets, age range, transfer/wage limits and player-interest settings. See [adapting the pack to your league](league-selection.md) before saving a club-specific copy.

## Updating an earlier installation

The current names have no `Chase` prefix. Move earlier prefixed copies and sample/test filters out of the game's two folders before copying the current pack. Keep any personal club-specific filters you created.

If you previously imported a view, import the current file again. FM may retain an older imported entry even after its file is moved. Restart FM if its file list has not refreshed. This update contains 54 current filters and 36 views; the old sample exports and two WB(R) prototypes are not part of it.

## If something looks wrong

- **Files absent:** check the folder names, your active user-data location and extra nesting.
- **Few or no players:** check minutes, league restrictions, scouting knowledge and player-interest switches. Use Early for diagnosis and inspect the resulting minute samples.
- **Too many players:** add markets and affordability, then compare candidates in the matching view. A broad Early pool is expected.
- **Blank stats:** check whether that player/competition has usable data in your save. Missing information is not evidence of poor performance.
- **Unexpected position or threshold:** compare with the [criteria guide](profiles.md) and report the exact file and displayed condition.

Built for FM27 Steam build 26340721 on Windows. The [validation notes](validation.md) state what has been checked in-game. No plugin or mod loader is needed to import these files.
