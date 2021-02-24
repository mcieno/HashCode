package main

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"strings"
	"sync"
	"time"
)

// Represents a pizza as a set of ingredients
type Pizza struct {
	id          int          // The sequence ID of this pizza
	I           int          // The number of ingredints this pizza is made of
	ingredients map[int]bool // The IDs of the ingredients in this pizza
}

// Represents an instance of the problem
type Problem struct {
	M             int            // Number of pizzas available
	T2            int            // Number of 2-person teams
	T3            int            // Number of 3-person teams
	T4            int            // Number of 4-person teams
	pizzas        []Pizza        // List of pizzas available
	ingredients   []string       // List of ingredients by name
	ingredientids map[string]int // Map from ingredient names to their IDs
}

// Represents an order, i.e., the pizzas a team will receive
type Order struct {
	score    int          // Score of this order
	pizzaids map[int]bool // Set of pizza IDs in this order
}

// Represents a solution to the problem, i.e., a list of orders delivered to teams
type Solution []Order

func Parse(filename string) Problem {

	input, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	lines := strings.Split(string(input), "\n")
	header, dataset := lines[0], lines[1:]

	var M, T2, T3, T4 int
	if _, err := fmt.Sscanf(header, "%d %d %d %d", &M, &T2, &T3, &T4); err != nil {
		panic(err)
	}

	pizzas := make([]Pizza, M)
	ingredients := make([]string, 0)
	ingredientids := make(map[string]int)

	for i := range pizzas {
		pizzainfo := strings.Split(dataset[i], " ")

		var I int
		if _, err := fmt.Sscanf(pizzainfo[0], "%d", &I); err != nil {
			panic(err)
		}

		pizzaingredients := make(map[int]bool)

		for k := 1; k <= I; k++ {
			ingredientName := pizzainfo[k]
			if _, found := ingredientids[ingredientName]; !found {
				ingredientids[ingredientName] = len(ingredients)
				ingredients = append(ingredients, ingredientName)
			}

			pizzaingredients[ingredientids[ingredientName]] = true
		}

		pizzas[i] = Pizza{
			id:          i,
			I:           I,
			ingredients: pizzaingredients,
		}
	}

	return Problem{
		M:             M,
		T2:            T2,
		T3:            T3,
		T4:            T4,
		pizzas:        pizzas,
		ingredients:   ingredients,
		ingredientids: ingredientids,
	}
}

// Exports the solution to a file.
func (problem *Problem) Export(solution Solution, filename string) {
	sol := ""
	sol += fmt.Sprintf("%d\n", len(solution))

	for _, order := range solution {
		sol += fmt.Sprint(len(order.pizzaids))
		for pid := range order.pizzaids {
			sol += fmt.Sprintf(" %d", pid)
		}
		sol += "\n"
	}

	bytes := []byte(sol)
	if err := ioutil.WriteFile(filename, bytes, 0644); err != nil {
		panic(err)
	}
}

func (problem Problem) Import(filename string) (Solution, int) {

	input, err := ioutil.ReadFile(filename)
	if err != nil {
		panic(err)
	}

	lines := strings.Split(string(input), "\n")
	header, dataset := lines[0], lines[1:]

	var T int
	if _, err := fmt.Sscanf(header, "%d", &T); err != nil {
		panic(err)
	}

	solution := make(Solution, T)

	for i := 0; i < T; i++ {
		orderinfo := strings.Split(dataset[i], " ")

		var Tsize int
		if _, err := fmt.Sscanf(orderinfo[0], "%d", &Tsize); err != nil {
			panic(err)
		}

		pizzaids := make(map[int]bool)

		for k := 1; k <= Tsize; k++ {
			var pid int
			if _, err := fmt.Sscanf(orderinfo[k], "%d", &pid); err != nil {
				panic(err)
			}
			pizzaids[pid] = true
		}

		allingredients := make(map[int]bool)
		for j, exists := range pizzaids {
			if exists {
				allingredients = Union(
					allingredients,
					problem.pizzas[j].ingredients,
				)
			}
		}

		solution[i] = Order{
			score:    len(allingredients) * len(allingredients),
			pizzaids: pizzaids,
		}
	}

	score := 0
	for _, order := range solution {
		score += order.score
	}

	return solution, score
}

// Returns the union of the given sets
func Union(sets ...map[int]bool) map[int]bool {
	u := make(map[int]bool)
	for _, set := range sets {
		for e, exists := range set {
			if exists {
				u[e] = true
			}
		}
	}

	return u
}

// Returns the intersection of the given sets
func Intersection(set1 map[int]bool, sets ...map[int]bool) map[int]bool {
	i := make(map[int]bool)

	for e, exists := range set1 {
		if exists {
			isinall := true
			for _, set := range sets[1:] {
				if exists, found := set[e]; !found || !exists {
					isinall = false
					break
				}
			}

			if isinall {
				i[e] = true
			}
		}
	}

	return i
}

func (problem Problem) RemovePizzaToOrder(pid int, order Order) Order {
	if _, found := order.pizzaids[pid]; !found {
		panic(fmt.Sprintf("Order %v does not have pizza %d", order, pid))
	}

	order.pizzaids[pid] = false
	delete(order.pizzaids, pid)

	// Recalculate order score
	allingredients := make(map[int]bool)
	for i, exists := range order.pizzaids {
		if exists {
			allingredients = Union(allingredients, problem.pizzas[i].ingredients)
		}
	}

	order.score = len(allingredients) * len(allingredients)

	return order
}

func (problem Problem) AddPizzaToOrder(pid int, order Order) Order {
	if _, found := order.pizzaids[pid]; found {
		panic(fmt.Sprintf("Order %v already has pizza %d", order, pid))
	}

	order.pizzaids[pid] = true

	// Recalculate order score
	allingredients := make(map[int]bool)
	for i, exists := range order.pizzaids {
		if exists {
			allingredients = Union(allingredients, problem.pizzas[i].ingredients)
		}
	}

	order.score = len(allingredients) * len(allingredients)

	return order
}

// Builds an order with random remaining pizzas.
func (problem Problem) RandomOrder(rpizzaids map[int]bool, osize int) (Order, map[int]bool) {
	if osize < 1 {
		panic("An order must contain pizzas")
	}

	if osize > len(rpizzaids) {
		panic("Not enough pizzas")
	}

	order := Order{
		score:    0,
		pizzaids: make(map[int]bool),
	}

	for i := 0; i < osize; i++ {
		// Select a random pizza and add it to the order
		for rpid := range rpizzaids {
			order = problem.AddPizzaToOrder(rpid, order)
			delete(rpizzaids, rpid)
			break
		}
	}

	return order, rpizzaids
}

// Deep copies an order
func (order Order) Clone() Order {
	clone := Order{score: order.score, pizzaids: make(map[int]bool)}
	for k, v := range order.pizzaids {
		clone.pizzaids[k] = v
	}

	return clone
}

// Finds the best possible order of size "osize" by bruteforcing the first 2
// pizzas and then greedily searching the remaining "osize - 2" ones.
func (problem Problem) BestOrder2(rpizzaids map[int]bool, osize int) (Order, map[int]bool) {
	if osize < 2 {
		panic("An order must contain pizzas 2+ pizzas")
	}

	if osize > len(rpizzaids) {
		panic("Not enough pizzas")
	}

	order := Order{
		score:    0,
		pizzaids: make(map[int]bool),
	}

	// Add 2 random pizzas to the order
	for rpid := range rpizzaids {
		order = problem.AddPizzaToOrder(rpid, order)
		delete(rpizzaids, rpid)
		break
	}

	for rpid := range rpizzaids {
		if exists, found := order.pizzaids[rpid]; !found || !exists {
			order = problem.AddPizzaToOrder(rpid, order)
			delete(rpizzaids, rpid)
			break
		}
	}

	for rpid := range rpizzaids {
		for rrpid := range rpizzaids {
			if rpid < rrpid {
				combined := Union(
					problem.pizzas[rpid].ingredients,
					problem.pizzas[rrpid].ingredients,
				)
				newscore := len(combined) * len(combined)
				if newscore > order.score {
					order = Order{
						score:    newscore,
						pizzaids: map[int]bool{rpid: true, rrpid: true},
					}
				}
			}
		}
	}

	for pid := range order.pizzaids {
		delete(rpizzaids, pid)
	}

	for len(order.pizzaids) < osize {
		// Add the pizza that increases the order score the most
		var bestrpid int
		for rpid := range rpizzaids {
			bestrpid = rpid
			break
		}

		bestorder := order.Clone()
		problem.AddPizzaToOrder(bestrpid, bestorder)
		bestscore := bestorder.score

		for rpid := range rpizzaids {
			tentativeorder := order.Clone()
			problem.AddPizzaToOrder(rpid, tentativeorder)
			if tentativeorder.score > bestscore {
				bestrpid = rpid
				bestscore = tentativeorder.score
			}
		}

		problem.AddPizzaToOrder(bestrpid, order)
		delete(rpizzaids, bestrpid)
	}

	return order, rpizzaids
}

// Builds an order with the "best" remaining pizza. That is, the pizzas with the most ingredients.
func (problem Problem) MostIngredientsOrder(rpizzaids map[int]bool, osize int) (Order, map[int]bool) {
	if osize < 1 {
		panic("An order must contain pizzas")
	}

	if osize > len(rpizzaids) {
		panic("Not enough pizzas")
	}

	order := Order{
		score:    0,
		pizzaids: make(map[int]bool),
	}

	for i := 0; i < osize; i++ {
		bestpid := -1
		for rpid := range rpizzaids {
			if bestpid == -1 || len(problem.pizzas[rpid].ingredients) > len(problem.pizzas[bestpid].ingredients) {
				bestpid = rpid
			}
		}
		order = problem.AddPizzaToOrder(bestpid, order)
		delete(rpizzaids, bestpid)
	}

	return order, rpizzaids
}

func (problem Problem) Solve() (Solution, int) {
	solution := make(Solution, 0)

	// Number of remaining teams for each size
	rT2, rT3, rT4 := problem.T2, problem.T3, problem.T4

	// IDs of remaining pizzas
	rpizzaids := make(map[int]bool)
	for i := 0; i < problem.M; i++ {
		rpizzaids[i] = true
	}

	iteration := 0
	for len(rpizzaids) > 1 && (rT2 > 0 || rT3 > 0 || rT4 > 0) {
		iteration++
		if iteration%10000 == 0 {
			fmt.Println("Iteration", iteration, "Remaining pizzas:", len(rpizzaids), "Remaining teams:", rT2+rT3+rT4)
		}

		var chosenorder Order

		switch iteration%3 + 2 {
		case 2:
			if rT2 == 0 || len(rpizzaids) < 2 {
				continue
			}
			rT2--

			// Let's satisfy a 2-person team
			//chosenorder, rpizzaids = problem.RandomOrder(rpizzaids, 2)
			chosenorder, rpizzaids = problem.MostIngredientsOrder(rpizzaids, 2)

		case 3:
			if rT3 == 0 || len(rpizzaids) < 3 {
				continue
			}
			rT3--

			// Let's satisfy a 3-person team
			//chosenorder, rpizzaids = problem.RandomOrder(rpizzaids, 3)
			chosenorder, rpizzaids = problem.MostIngredientsOrder(rpizzaids, 3)

		case 4:
			if rT4 == 0 || len(rpizzaids) < 4 {
				continue
			}
			rT4--

			// Let's satisfy a 4-person team
			//chosenorder, rpizzaids = problem.RandomOrder(rpizzaids, 4)
			chosenorder, rpizzaids = problem.MostIngredientsOrder(rpizzaids, 4)

		default:
			panic("No teams left")
		}

		solution = append(solution, chosenorder)
	}

	score := 0
	for _, order := range solution {
		score += order.score
	}

	return solution, score
}

// Returns the score of a solution
func (solution Solution) Score() int {
	score := 0
	for _, order := range solution {
		score += order.score
	}

	return score
}

// Returns the number of remaining n-person teams and the set of remaining pizzas
func (problem Problem) Remaining(solution Solution) (int, int, int, map[int]bool) {
	rT2, rT3, rT4 := problem.T2, problem.T3, problem.T4

	upizzaids := make(map[int]bool)
	for _, order := range solution {
		switch len(order.pizzaids) {
		case 2:
			rT2++
		case 3:
			rT3++
		case 4:
			rT4++
		}
		for pid := range order.pizzaids {
			upizzaids[pid] = true
		}
	}

	rpizzaids := make(map[int]bool)
	for _, pizza := range problem.pizzas {
		if exists, found := upizzaids[pizza.id]; !found || !exists {
			rpizzaids[pizza.id] = true
		}
	}

	return rT2, rT3, rT4, rpizzaids
}

func (problem Problem) Improve(solution Solution, maxtime float64) (Solution, int) {
	score := solution.Score()

	start := time.Now()
	iteration := 0
	for time.Now().Sub(start).Seconds() < maxtime {
		iteration++
		if iteration%1000 == 0 {
			score = solution.Score()
			fmt.Println("Iteration", iteration, "Score:", score)
		}

		var i, j int
		i = rand.Intn(len(solution))
		j = rand.Intn(len(solution))
		for i == j {
			j = rand.Intn(len(solution))
		}

		scorebefore := solution[i].score + solution[j].score

		var ipid, jpid int
		for k, exists := range solution[i].pizzaids {
			if exists {
				ipid = k
				break
			}
		}
		for k, exists := range solution[j].pizzaids {
			if exists {
				jpid = k
				break
			}
		}

		solution[i] = problem.RemovePizzaToOrder(ipid, solution[i])
		solution[j] = problem.RemovePizzaToOrder(jpid, solution[j])
		solution[i] = problem.AddPizzaToOrder(jpid, solution[i])
		solution[j] = problem.AddPizzaToOrder(ipid, solution[j])

		scoreafter := solution[i].score + solution[j].score

		if scoreafter <= scorebefore {
			solution[i] = problem.RemovePizzaToOrder(jpid, solution[i])
			solution[j] = problem.RemovePizzaToOrder(ipid, solution[j])
			solution[i] = problem.AddPizzaToOrder(ipid, solution[i])
			solution[j] = problem.AddPizzaToOrder(jpid, solution[j])
		} else {
			fmt.Println("+", (scoreafter - scorebefore), "by swapping", ipid, jpid, "in orders", i, j)
			score += (scoreafter - scorebefore)
		}
	}

	return solution, score
}

func main() {
	// identifier: { input_file, output_file, solution_to_optimize }
	dataset := map[string][]string{
		//"a": {"in/a.txt", "out/a.txt", "out/a.txt"},
		"b": {"in/b.txt", "out/b.txt", "out/b.txt"},
		"c": {"in/c.txt", "out/c.txt", "out/c.txt"},
		"d": {"in/d.txt", "out/d.txt", "out/d.txt"},
		"e": {"in/e.txt", "out/e.txt", "out/e.txt"},
	}

	var wg sync.WaitGroup
	totalscore := 0

	for letter, files := range dataset {
		wg.Add(1)
		go func(letter, infile, outfile, tooptimize string) {
			problem := Parse(infile)
			fmt.Println(
				letter,
				"[*] Problem parsed from file:",
				problem.M,
				problem.T2,
				problem.T3,
				problem.T4,
			)

			fmt.Println(letter, "[*] Importing...")
			solution, score := problem.Import(tooptimize)
			fmt.Println(
				letter,
				"[*] Solution imported - score:",
				score,
			)

			isolution, iscore := problem.Improve(solution, 3600) // 1 hour
			fmt.Println(letter, "[*] Final solution has score", iscore)

			problem.Export(isolution, fmt.Sprintf("%s%d", outfile, iscore))
			fmt.Println(
				letter,
				"[*] Solution written to",
				fmt.Sprintf("%s%d", outfile, iscore),
			)

			wg.Add(1)
			totalscore += score
			wg.Done()
		}(letter, files[0], files[1], files[2])
	}

	wg.Wait()

	fmt.Println("*** TOTAL SCORE:", totalscore)
}
