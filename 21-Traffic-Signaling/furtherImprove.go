package main

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	MethodA = iota
	MethodB = iota
	MethodC = iota
	MethodD = iota
	MethodE = iota
	MethodF = iota
)

// A Street, described by the intersection it originates from (B), the
// intersection it arrives to (E), a length (L) and a unique name.
type Street struct {
	id   int    // ID of the street itself
	B    int    // ID of the intersection where the street begins
	E    int    // ID of the intersection where the street ends
	L    int    // Time required to get from B to E
	name string // name of the street (used when printing the solution)
}

// An Intersection, described by the set of incoming and the set of outgoing
// streets.
type Intersection struct {
	id       int   // ID of the intersection itself
	incoming []int // Set of street IDs that end in this intersection
	outgoing []int // Set of street IDs that begin in this intersection
}

// A Vehicle, described by the path the car has to drive.
type Vehicle struct {
	id   int   // ID of the vehicle itself.
	path []int // List of street ids the vehicle must travel.
}

// A convenient Problem object to pass around
type Problem struct {
	D             int            // Duration of the simulation
	I             int            // Number of Intersections
	S             int            // Number of Streets
	V             int            // Number of Vehicles
	F             int            // Bonus points for reaching destination
	streets       []Street       // The main data structure representing the problem input is a collection of streets (by ID)
	streetids     map[string]int // A map from names to IDs to do reverse lookups
	intersections []Intersection // All intersections of the map
	vehicles      []Vehicle      // All vehicles in the simulation
}

// The Schedule of an intersection is described by the ID of the intersection
// and the array of semaphores of the streets belonging to that intersection.
type Schedule struct {
	id      int   // ID of the intersection this schedule is for
	streets []int // List of street IDs in this intersection whose semaphores are part of the schedule
	tgreens []int // List of times each of the corresponding street semaphore remains green
}

// A solution is a map from intersection IDs to its schedule.
type Solution map[int]Schedule

// Represents a vehicle arriving to an intersection at a certain time
type Arrival struct {
	t   int // Time the vehicle will arrive
	vid int // ID of the vehicle
	pid int // Index in the vehicle path of the street this vehicle will arrive at
}

// A map from time to the list of arrivals at that time.
type Simulation map[int][]Arrival

// Simulation statistics
type SimulationStatistics struct {
	jampeaks map[int]int // Map from street id to the maximum number of vehicles simultaneously queued at its semaphore during the simulation.
}

// A map from street id to the queue of vehicle IDs waiting at the semaphore.
type SemaphoreQueues map[int](chan int)

func Parse(filename string) Problem {

	input, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	lines := strings.Split(string(input), "\n")
	header, dataset := lines[0], lines[1:]

	var D, I, S, V, F int
	if _, err := fmt.Sscanf(header, "%d %d %d %d %d", &D, &I, &S, &V, &F); err != nil {
		panic(err)
	}

	streetsData, vehiclesData := dataset[:S], dataset[S:]

	streets := make([]Street, S)
	streetids := make(map[string]int)

	intersections := make([]Intersection, I)
	for i := range intersections {
		intersections[i] = Intersection{
			incoming: make([]int, 0),
			outgoing: make([]int, 0),
		}
	}

	for k, streetdata := range streetsData {
		var b, e, l int
		var name string

		if _, err := fmt.Sscanf(streetdata, "%d %d %s %d", &b, &e, &name, &l); err != nil {
			panic(err)
		}

		st := Street{B: b, E: e, L: l, name: name}

		streets[k] = st
		streetids[name] = k
		intersections[st.E].incoming = append(intersections[st.E].incoming, k)
		intersections[st.B].outgoing = append(intersections[st.B].outgoing, k)
	}

	vehicles := make([]Vehicle, V)

	for i := range vehicles {
		pathspec := strings.Split(vehiclesData[i], " ")
		nstreetsstr, streetnames := pathspec[0], pathspec[1:]

		var nstreets int
		if _, err := fmt.Sscanf(nstreetsstr, "%d", &nstreets); err != nil {
			panic(err)
		}

		path := make([]int, nstreets)
		for k, name := range streetnames {
			path[k] = streetids[name]
		}

		vehicles[i] = Vehicle{id: i, path: path}
	}

	for _, vehicle := range vehicles {
		for i, p := range vehicle.path {
			for _, pp := range vehicle.path[i+1:] {
				if p == pp {
					panic("Same street in path")
				}
			}
		}
	}

	return Problem{
		D:             D,
		I:             I,
		S:             S,
		V:             V,
		F:             F,
		streets:       streets,
		streetids:     streetids,
		intersections: intersections,
		vehicles:      vehicles,
	}
}

func (problem *Problem) Validate(solution Solution) {
	if len(solution) > problem.I {
		fmt.Println(len(solution), problem.I)
		panic("Too many schedules in solution")
	}

	for iid, schedule := range solution {
		if iid != schedule.id {
			fmt.Println(iid, schedule.id)
			panic("Intersection ID mismatch")
		}

		if iid < 0 || iid >= problem.I {
			fmt.Println(iid, problem.I)
			panic("Invalid intersection ID")
		}

		if len(schedule.streets) != len(schedule.tgreens) {
			fmt.Println(len(schedule.streets), len(schedule.tgreens))
			panic("Different lengths of schedule.streets and schedule.tgreens")
		}

		if len(schedule.streets) == 0 {
			panic("Empty schedule")
		}

		if len(schedule.streets) > len(problem.intersections[iid].incoming) {
			fmt.Println(schedule.streets, problem.intersections[iid].incoming)
			panic("Too many streets in schedule")
		}

		for _, sid := range schedule.streets {
			if problem.streets[sid].E != iid {
				fmt.Println(iid, problem.streets[sid])
				panic("Schedule for semaphore not in this intersection")
			}
		}

		tottime := 0
		for _, tgreen := range schedule.tgreens {
			if tgreen < 1 {
				panic("Bad time for green light")
			}

			tottime += tgreen

			if tottime > problem.D {
				panic("Too long schedule")
			}
		}
	}
}

// Registers the fact that vehicle with ID `vid` will arrive at the semaphore of
// street whose index in its whole path is `pid` at time `t`.
func (simulation Simulation) RegisterArrival(t int, arrival Arrival) {
	if _, found := simulation[t]; !found {
		simulation[t] = make([]Arrival, 0)
	}

	simulation[t] = append(simulation[t], arrival)
}

// Get arrivals at time `t`
func (simulation Simulation) GetArrivals(t int) []Arrival {
	if _, found := simulation[t]; !found {
		return make([]Arrival, 0)
	}

	return simulation[t]
}

// Add a vehicle to the queue of the semaphore at the end of street whose ID is
// `sid`.
func (queues SemaphoreQueues) Enqueue(sid, vid int) {
	if _, found := queues[sid]; !found {
		queues[sid] = make(chan int, 1000) // Always <= 1000 vehicles queued
	}

	queues[sid] <- vid
}

// Pops the vehicle from the front of the queue of the semaphore at the end of
// street whose ID is `sid`.
// Returns the vehicle ID and true/false depending on whether there was an
// element do pop or not.
func (queues SemaphoreQueues) Dequeue(sid int) (int, bool) {
	if queue, found := queues[sid]; !found || len(queue) == 0 {
		return -1, false
	}

	return <-queues[sid], true
}

// Simulates the solution and returns the Simulation result and the score.
func (problem *Problem) Simulate(solution Solution) (int, SimulationStatistics) {
	problem.Validate(solution)

	simulation := make(Simulation)
	queues := make(SemaphoreQueues)

	stats := SimulationStatistics{
		jampeaks: make(map[int]int),
	}

	// Initialize so that at instant 0 each vehicle will be queued at the
	// semaphore of the first street in their path.
	for vid := range problem.vehicles {
		simulation.RegisterArrival(0, Arrival{t: 0, vid: vid, pid: 0})
	}

	score := 0
	for now := 0; now < problem.D; now++ {
		for _, arrival := range simulation.GetArrivals(now) {
			queues.Enqueue(
				problem.vehicles[arrival.vid].path[arrival.pid],
				arrival.vid,
			)
		}

		for sid := range problem.streets {
			if peak, found := stats.jampeaks[sid]; len(queues[sid]) > 0 && (!found || len(queues[sid]) > peak) {
				stats.jampeaks[sid] = len(queues[sid])
			}
		}

		for _, schedule := range solution {
			sid := schedule.WhichGreen(now)
			if vid, any := queues.Dequeue(sid); any {
				// If this was the last street for vehicle vid, update score.
				// Otherwise, register its arrival to the next intersection.
				for pid, currsid := range problem.vehicles[vid].path {
					if currsid == sid {
						nextsid := problem.vehicles[vid].path[pid+1]
						if pid == len(problem.vehicles[vid].path)-2 {
							if now+problem.streets[nextsid].L <= problem.D {
								score += problem.F + (problem.D - now - problem.streets[nextsid].L)
							}
						} else if now+problem.streets[nextsid].L < problem.D {
							simulation.RegisterArrival(
								now+problem.streets[nextsid].L,
								Arrival{
									t:   now + problem.streets[nextsid].L,
									vid: vid,
									pid: pid + 1,
								},
							)
						}
						break
					}
				}
			}
		}
	}

	return score, stats
}

// Exports the solution to a file.
func (problem *Problem) Export(solution Solution, filename string) {
	sol := ""
	sol += strconv.FormatInt(int64(len(solution)), 10) + "\n"

	for intersection, schedule := range solution {
		sol += strconv.FormatInt(int64(intersection), 10) + "\n" + strconv.FormatInt(int64(len(schedule.streets)), 10) + "\n"
		for i, sid := range schedule.streets {
			sol += problem.streets[sid].name + " " + strconv.FormatInt(int64(schedule.tgreens[i]), 10) + "\n"
		}
	}

	bytes := []byte(sol)
	if err := ioutil.WriteFile(filename, bytes, 0644); err != nil {
		panic(err)
	}
}

// Exports the solution to a file.
func (problem *Problem) Import(filename string) Solution {

	input, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	solution := make(Solution)

	lines := strings.Split(string(input), "\n")
	header, solutionset := lines[0], lines[1:]
	var count int
	if _, err := fmt.Sscanf(header, "%d", &count); err != nil {
		panic(err)
	}

	for i := 0; i < count; i++ {
		var iid int
		if _, err := fmt.Sscanf(solutionset[0], "%d", &iid); err != nil {
			panic(err)
		}

		var size int
		if _, err := fmt.Sscanf(solutionset[1], "%d", &size); err != nil {
			panic(err)
		}

		solution[iid] = Schedule{
			id:      iid,
			streets: make([]int, size),
			tgreens: make([]int, size),
		}

		for k := 0; k < size; k++ {
			var streetname string
			var tgreen int
			if _, err := fmt.Sscanf(solutionset[2+k], "%s %d", &streetname, &tgreen); err != nil {
				panic(err)
			}

			solution[iid].streets[k] = problem.streetids[streetname]
			solution[iid].tgreens[k] = tgreen
		}

		solutionset = solutionset[2+size:]
	}

	return solution
}

// Returns the duration of a schedule.
func (schedule Schedule) Duration() int {
	acc := 0
	for _, t := range schedule.tgreens {
		acc += t
	}
	return acc
}

// Returns the ID of the semaphore that is green at a certain moment.
func (schedule Schedule) WhichGreen(when int) int {
	when %= schedule.Duration()

	acc := 0
	for i, t := range schedule.tgreens {
		acc += t
		if acc > when {
			return schedule.streets[i]
		}
	}

	panic("Unknown error")
}

// Returns true if at least one vehicle has the street in its path.
func (problem Problem) IsStreetUsed(streetid int) bool {
	for _, vehicle := range problem.vehicles {
		for _, sid := range vehicle.path {
			if streetid == sid {
				return true
			}
		}
	}

	return false
}

func (problem Problem) TrivialSolve() Solution {
	solution := make(map[int]Schedule)

	for iid, intersection := range problem.intersections {
		schedule := Schedule{
			id:      iid,
			streets: make([]int, 0),
			tgreens: make([]int, 0),
		}

		for _, incomingSid := range intersection.incoming {
			if problem.IsStreetUsed(incomingSid) {
				schedule.streets = append(
					schedule.streets,
					incomingSid,
				)
				schedule.tgreens = append(
					schedule.tgreens,
					1,
				)
			}
		}

		if len(schedule.tgreens) > 0 {
			solution[iid] = schedule
		}
	}

	return solution
}

func (problem Problem) Solve(method int) Solution {
	var solution Solution

	switch method {
	case MethodA:
		solution = Solution{
			1: Schedule{
				id:      1,
				streets: []int{2, 1},
				tgreens: []int{1, 1},
			},
			0: Schedule{
				id:      0,
				streets: []int{0},
				tgreens: []int{1},
			},
			2: Schedule{
				id:      2,
				streets: []int{4},
				tgreens: []int{1},
			},
		}
	case MethodB:
		fallthrough
	case MethodC:
		fallthrough
	case MethodD:
		fallthrough
	case MethodE:
		fallthrough
	case MethodF:
		fallthrough
	default:
		solution = problem.TrivialSolve()
	}

	return solution
}

func RankMap(values map[int]int) []int {
	type kv struct {
		Key   int
		Value int
	}

	var ss []kv

	for k, v := range values {
		ss = append(ss, kv{k, v})
	}

	sort.Slice(ss, func(i, j int) bool {
		return ss[i].Value > ss[j].Value
	})

	ranked := make([]int, len(values))
	for i, kv := range ss {
		ranked[i] = kv.Key
	}

	return ranked
}

func (problem Problem) ImproveRandom(solution Solution, maxtime float64) Solution {
	score, _ := problem.Simulate(solution)

	max := int(problem.S/200 + 1) // In one iteration we improve top 2% jammed streets
	fmt.Println("[*] Improving at most", max, "jams at once")

	start := time.Now()

	for time.Now().Sub(start).Seconds() < maxtime {
		var iscore int
		if rand.Intn(100) < 70 {
			// 10% of the times, try to improve
			fmt.Println("[*] Perform greedy improvements")
			solution = problem.Improve(solution, maxtime/50+1)
			fmt.Println("[*] Greedy improvements completed")
			iscore, _ = problem.Simulate(solution)
		} else {
			// 90% of the times, randomize
			fmt.Println("[*] Randomizing schedules")

			backupiids := make(chan int, max)
			backupstreets := make(chan []int, max)
			backuptgreens := make(chan []int, max)

			for __ := 0; __ < rand.Intn(max); __++ {
				// This for-loop is just a trick to get a random entry
				for iid, schedule := range solution {
					copystreets := make([]int, len(solution[iid].streets))
					copytgreens := make([]int, len(solution[iid].tgreens))
					copy(copystreets, solution[iid].streets)
					copy(copytgreens, solution[iid].tgreens)
					backupiids <- iid
					backupstreets <- copystreets
					backuptgreens <- copytgreens
					for i := 0; i < int(len(schedule.streets)/2); i++ {
						j := rand.Intn(len(schedule.streets))
						solution[iid].streets[i], solution[iid].streets[j] = solution[iid].streets[j], solution[iid].streets[i]
						solution[iid].tgreens[i], solution[iid].tgreens[j] = solution[iid].tgreens[j], solution[iid].tgreens[i]
					}

					break
				}
			}
			iscore, _ = problem.Simulate(solution)
			fmt.Println("[*] Randomization completed:", iscore)
			if iscore < score {
				fmt.Println("[*] Unlucky randomization. Restoring...")
				for len(backupiids) > 0 {
					iid := <-backupiids
					copy(solution[iid].streets, <-backupstreets)
					copy(solution[iid].tgreens, <-backuptgreens)
				}
			}
		}

		if iscore > score {
			fmt.Printf(
				"[*] Improvement (%d): %d\n",
				max,
				iscore,
			)
			score = iscore
		}
	}

	return solution
}

func (problem Problem) ImproveJams(solution Solution, maxtime float64) Solution {
	score, stats := problem.Simulate(solution)

	max := int(problem.S/200 + 1) // In one iteration we improve top 2% jammed streets
	fmt.Println("[*] Improving at most", max, "jams at once")

	start := time.Now()

	for time.Now().Sub(start).Seconds() < maxtime {
		if max <= 2 {
			max = int(problem.S/200 + 1)
			if rand.Intn(100) < 70 {
				// 70% of the times, try to improve
				fmt.Println("[*] Perform greedy improvements")
				solution = problem.Improve(solution, maxtime/20)
				score, stats = problem.Simulate(solution)
				fmt.Println("[*] Greedy improvements completed")
			} else {
				// 30% of the times, randomize
				fmt.Println("[*] Randomizing schedules")
				for __ := 0; __ < rand.Intn(max); __++ {
					// This for-loop is just a trick to get a random entry
					for iid, schedule := range solution {
						for i := 0; i < int(len(schedule.streets)/2); i++ {
							j := rand.Intn(len(schedule.streets))
							solution[iid].streets[i], solution[iid].streets[j] = solution[iid].streets[j], solution[iid].streets[i]
							solution[iid].tgreens[i], solution[iid].tgreens[j] = solution[iid].tgreens[j], solution[iid].tgreens[i]
						}

						break
					}
				}
				score, stats = problem.Simulate(solution)
				fmt.Println("[*] Randomization completed:", score)
			}
		}
		topjammed := RankMap(stats.jampeaks)

		for i := 0; i < max; i++ {
			sid := topjammed[i]
			iid := problem.streets[sid].E
			if schedule, found := solution[iid]; found && schedule.Duration() < problem.D {
				for k, s := range schedule.streets {
					if s == sid {
						solution[iid].tgreens[k]++
					}
					break
				}
			} else {
				topjammed[i] = -1
			}
		}

		iscore, istats := problem.Simulate(solution)
		if iscore > score {
			fmt.Printf(
				"[*] Improvement (%d): %d\n",
				max,
				iscore,
			)
			score = iscore
			stats = istats
		} else {
			// Revert and lower max
			for i := 0; i < max; i++ {
				if sid := topjammed[i]; sid != -1 {
					iid := problem.streets[sid].E
					for k, s := range solution[iid].streets {
						if s == sid {
							solution[iid].tgreens[k]--
						}
						break
					}
				}
			}

			max = int(max/2) + 1
		}
	}

	return solution
}

func (problem Problem) Improve(solution Solution, maxtime float64) Solution {
	score, _ := problem.Simulate(solution)

	start := time.Now()

	for time.Now().Sub(start).Seconds() < maxtime {
		anyimprovement := false
		for iid := range solution {
			if solution[iid].Duration() >= problem.D {
				continue
			}

			for k := range solution[iid].tgreens {
				solution[iid].tgreens[k]++
				iscore, _ := problem.Simulate(solution)
				for iscore > score {
					anyimprovement = true
					score = iscore
					fmt.Printf(
						"[*] Improvement (iid %d, street %d, tgreen %d): %d\n",
						iid,
						solution[iid].streets[k],
						solution[iid].tgreens[k],
						iscore,
					)
					solution[iid].tgreens[k]++
					iscore, _ = problem.Simulate(solution)
					if solution[iid].Duration() >= problem.D {
						break
					}

					if time.Now().Sub(start).Seconds() > maxtime {
						break
					}
				}
				solution[iid].tgreens[k]--

				if time.Now().Sub(start).Seconds() > maxtime {
					break
				}
			}

			if time.Now().Sub(start).Seconds() > maxtime {
				break
			}
		}

		if !anyimprovement {
			break
		}
	}

	return solution
}

func main() {
	// identifier: { input_file, output_file, solution_to_optimize }
	dataset := map[string][]string{
		//"a": {"in/a.txt", "out/a.txt", "out/a.txt"},
		"b": {"in/b.txt", "out/b.txt", "out/b.txt"},
		"c": {"in/c.txt", "out/c.txt", "out/c.txt"},
		"d": {"in/d.txt", "out/d.txt", "out/d.txt"},
		"e": {"in/e.txt", "out/e.txt", "out/e.txt"},
		"f": {"in/f.txt", "out/f.txt", "out/f.txt"},
	}

	for letter, files := range dataset {
		problem := Parse(files[0])
		fmt.Println(
			letter,
			"[*] Problem parsed from file:",
			problem.D,
			problem.F,
			problem.I,
			problem.S,
			problem.V,
		)

		fmt.Println(letter, "[*] Importing...")
		solution := problem.Import(files[2])
		score, _ := problem.Simulate(solution)
		fmt.Println(
			letter,
			"[*] Solution imported - score:",
			score,
		)

		isolution := problem.ImproveRandom(solution, 3600) // 1 hour
		iscore, _ := problem.Simulate(isolution)
		fmt.Println("[*] Final solution has score", iscore)

		problem.Export(isolution, fmt.Sprintf("%s%d", files[1], iscore))
		fmt.Println(
			letter,
			"[*] Solution written to",
			fmt.Sprintf("%s%d", files[1], iscore),
		)
	}
}
