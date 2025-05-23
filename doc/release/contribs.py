# https://github.com/networkx/networkx/pull/2542
# https://github.com/scikit-image/scikit-image/blob/main/tools/generate_release_notes.py
from subprocess import check_output
import sys
import shlex

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print(
        "Usage: ./contributors.py tag-of-previous-release tag-of-newer-release (optional)"
    )
    sys.exit(-1)

tag = sys.argv[1]
if len(sys.argv) < 3:
    compare_tag = None
else:
    compare_tag = sys.argv[2]


def call(cmd):
    return check_output(shlex.split(cmd), text=True).split("\n")


tag_date = call(f"git log -n1 --format='%ci' {tag}")[0]
if compare_tag:
    compare_tag_date = call(f"git log -n1 --format='%ci' {compare_tag}")[0]

print(f"Release {tag} was on {tag_date}\n")

if compare_tag:
    merges = call(
        f"git log --since='{tag_date}' --until='{compare_tag_date}' --merges --format='>>>%B' --reverse"
    )
else:
    merges = call(f"git log --since='{tag_date}' --merges --format='>>>%B' --reverse")
merges = [m for m in merges if m.strip()]
merges = "\n".join(merges).split(">>>")
merges = [m.split("\n")[:2] for m in merges]
merges = [m for m in merges if len(m) == 2 and m[1].strip()]

if compare_tag:
    num_commits = call(f"git rev-list {tag}..{compare_tag} --count")[0]
else:
    num_commits = call(f"git rev-list {tag}..HEAD --count")[0]

print(f"A total of {num_commits} changes have been committed.\n")

# Use filter to remove empty strings
if compare_tag:
    commits = filter(
        None,
        call(
            f"git log --since='{tag_date}' --until='{compare_tag_date}' --pretty=%s --reverse"
        ),
    )
else:
    commits = filter(
        None,
        call(f"git log --since='{tag_date}' --pretty=%s --reverse"),
    )
for c in commits:
    print("- " + c)

print(f"\nIt contained the following {len(merges)} merges:\n")
for merge, message in merges:
    if merge.startswith("Merge pull request #"):
        PR = f" ({merge.split()[3]})"
    else:
        PR = ""

    print("- " + message + PR)

print("\nMade by the following committers [alphabetical by last name]:\n")

if compare_tag:
    authors = call(
        f"git log --since='{tag_date}' --until='{compare_tag_date}' --format=%aN"
    )
else:
    authors = call(f"git log --since='{tag_date}' --format=%aN")
authors = [a.strip() for a in authors if a.strip()]


def key(author):
    author = list(author.split())
    if len(author) > 0:
        return author[-1]


authors = sorted(set(authors), key=key)

for a in authors:
    print("- " + a)
