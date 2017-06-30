# TeamCity python library

Incomplete but easy to extend. Implemented:

- get and set build configuration parameters
- trigger builds
- get basic agent info
- get builds
- get build queue

### Usage

```python
from TeamCity.TeamCity import TeamCity
tc = TeamCity()
tc.triggerBuild("build1")
```
### License

MIT license.
