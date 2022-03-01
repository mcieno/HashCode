package main

import (
	"bufio"
	"flag"
	"log"
	"os"
)

func main() {
	filename := flag.String("filename", "", "problem file")
	flag.Parse()

	fd, err := os.Open(*filename)
	if err != nil {
		log.Fatalf("unable to open file: %v", err)
	}

	p, err := LoadProblem(bufio.NewReader(fd))
	if err != nil {
		log.Fatalln("parse problem:", err)
	}

	sim := NewSimulation(*p)

	sol, score := sim.Run()
	log.Println("found solution with score", score)

	sol.Write(os.Stdout)
}
