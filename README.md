# Taskwarrior Input

## Getting Started

### Prerequisites

### Installing

## Built With

## Contribution Guidelines

### Workflow
Before committing, be sure to:
1. Use [Git Flow](https://www.atlassian.com/git/tutorials/comparing-workflows/gitflow-workflow)
2. [Sign your commits](https://git-scm.com/book/ms/v2/Git-Tools-Signing-Your-Work)
3. Run `gofmt -s -w .`

### Commit Messages
The rules of [conventional commit messages](https://www.conventionalcommits.org/en/v1.0.0-beta.2/) should be observed.
Observe to keep the first line of the commit message down to 50 characters and insert hard line-breaks at 72 characters
for the rest of the message body.

When working on `feature` or `hotfix` branches, the rules can be relaxed a bit. PRs should only be opened from your
`develop` branch, and when wrapping up your `feature` branches, you should squash your commits.

#### Tags
- fix&mdash;for bugfixes
- feat&mdash;for any new functionality
- BREAKING CHANGE&mdash;annotation in the commit message body for any changes that will affect backwards-compatability.
- refactor&mdash;for reworked code that ends up being functionally the same
- docs&mdash;for changes to docstrings, CHANGELOG.md, this README, etc.
- chore&mdash;for changes to the repo that don't affect functional code or
  docs (i.e. Makefiles, Dockerfiles, etc.)

## Versioning
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags).
Changes from version to version are tracked in [CHANGELOG.md](CHANGELOG.md).

## Authors

* **Robert Hawk** - *Initial work* - [DerHabicht](https://github.com/DerHabicht)

See also the list of [contributors](https://github.com/weblair/deploy/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* [PurpleBooth](https://github.com/PurpleBooth) for the README template
