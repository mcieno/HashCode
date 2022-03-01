package main

import (
	"fmt"
	"io"
	"log"
	"math"
	"sort"
	"strings"
)

type (
	Simulation struct {
		problem Problem
	}

	Solution struct {
		Projects  []Project
		Assignees [][]Contributor
	}
)

func NewSimulation(p Problem) Simulation {
	return Simulation{
		problem: p,
	}
}

func (s Simulation) Run() (sol Solution, score int) {
	freeAtTime := make(map[int]map[string]bool)

	freeNow := make(map[string]bool)
	for cName := range s.problem.Contributors {
		freeNow[cName] = true
	}

	todoProjects := make(map[string]bool)
	for pName := range s.problem.Projects {
		todoProjects[pName] = true
	}

	t := 0
	for {
		for t = range freeAtTime {
			break
		}
		for ft := range freeAtTime {
			if ft < t {
				t = ft
			}
		}

		log.Printf("time: %-10d score: %-10d todo: %-10d\n", t, score, len(todoProjects))

		for name := range freeAtTime[t] {
			freeNow[name] = true
		}

		delete(freeAtTime, t)

		if len(freeNow) == 0 {
			panic("wtf?")
		}

		for pName := range todoProjects {
			prj := s.problem.Projects[pName]
			if prj.ScoreIfNow(t) <= 0 {
				delete(todoProjects, pName)
			}
		}

		if len(todoProjects) == 0 {
			break
		}

		// Sort projects by best candidate
		var sortedTodoProjects []string
		for pName := range todoProjects {
			sortedTodoProjects = append(sortedTodoProjects, pName)
		}
		sort.Slice(sortedTodoProjects, func(i, j int) bool {
			iPrj := s.problem.Projects[sortedTodoProjects[i]]
			jPrj := s.problem.Projects[sortedTodoProjects[j]]

			return float64(iPrj.ScoreIfNow(t))/math.Pow(float64(iPrj.Duration), 0.3) >
				float64(jPrj.ScoreIfNow(t))/math.Pow(float64(jPrj.Duration), 0.3)
		})

		// Try assign contributors to a project
		for _, pName := range sortedTodoProjects {
			prj := s.problem.Projects[pName]
			toFill := make(map[int]bool)
			for i := range prj.Roles {
				toFill[i] = true
			}

			assignees := struct {
				count int
				names []string
				ctbs  []Contributor
			}{
				count: 0,
				names: make([]string, len(prj.Roles)),
				ctbs:  make([]Contributor, len(prj.Roles)),
			}

			for cName := range freeNow {
				ctb := s.problem.Contributors[cName]
				for i := range toFill {
					if ctb.CanFill(prj.Roles[i], assignees.ctbs) {
						assignees.ctbs[i] = ctb
						assignees.names[i] = cName
						assignees.count++
						delete(toFill, i)
						break
					}
				}

				if assignees.count == len(prj.Roles) {
					break
				}
			}

			if assignees.count == len(prj.Roles) {
				for i, aName := range assignees.names {
					a := assignees.ctbs[i]
					a.Fill(prj.Roles[i])
					s.problem.Contributors[aName] = a

					delete(freeNow, aName)
					if freeAtTime[t+prj.Duration] == nil {
						freeAtTime[t+prj.Duration] = make(map[string]bool)
					}

					freeAtTime[t+prj.Duration][aName] = true
				}

				sol.Assignees = append(sol.Assignees, assignees.ctbs)
				sol.Projects = append(sol.Projects, prj)

				score += prj.ScoreIfNow(t)
				delete(todoProjects, pName)
			}
		}

		if len(freeAtTime) == 0 || len(todoProjects) == 0 {
			break
		}
	}

	return sol, score
}

func (s *Solution) Write(w io.Writer) {
	fmt.Fprintf(w, "%d\n", len(s.Projects))

	for i, project := range s.Projects {
		fmt.Fprintf(w, "%s\n", project.Name)

		names := make([]string, 0)

		for _, assignee := range s.Assignees[i] {
			names = append(names, assignee.Name)
		}

		fmt.Fprintf(w, "%s\n", strings.Join(names, " "))
	}
}
