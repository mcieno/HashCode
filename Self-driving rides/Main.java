import java.io.File;
import java.io.FileNotFoundException;
import java.util.ArrayList;
import java.util.Scanner;

public class Main {

	public static void main(String[] args) {

		if (args.length != 1) {
			System.err.println("Expected exactly 1 command line argument.");
			System.exit(1);
		}

		Object[] info = parseInput(args[0]);

		@SuppressWarnings("unchecked")
		ArrayList<Vehicle> fleet = (ArrayList<Vehicle>) info[0];
		City city = (City) info[1];

		solve(fleet, city, 5);

		prettyPrint(fleet);
	}

	/**
	 * Solve the self-driving rides problem.
	 * 
	 * @param fleet
	 *            Fleet of vehicles in the scenario.
	 * @param city
	 *            City where the vehicles will pick up rides.
	 * @param threshold
	 *            Optimization threshold. Suggested value for all given test cases
	 *            is 5.
	 */
	private static void solve(ArrayList<Vehicle> fleet, City city, int threshold) {
		Vehicle freeCar = null;
		while ((freeCar = Vehicle.firstFree(fleet)).clock < city.maxtime) {
			Ride bestR = city.bestRide(freeCar);
			if (bestR != null) {
				freeCar.takeRide(bestR);
				city.taken[bestR.ID] = true;
			} else {
				freeCar.kill(city.maxtime);
			}
		}

		for (int t = 0; t < threshold; ++t) {
			for (Vehicle vehicle : fleet) {
				fleet.set(vehicle.ID, city.optimize(vehicle));
			}
		}
	}

	/**
	 * Print the fleet information in the format needed to submit the solution.
	 * 
	 * @param fleet
	 *            Fleet of vehicles in the scenario.
	 */
	private static void prettyPrint(ArrayList<Vehicle> fleet) {
		for (Vehicle vehicle : fleet) {
			System.out.println(vehicle);
		}
	}

	/**
	 * Parse the specified file and generate both the fleet and the city.
	 * 
	 * @param filename
	 *            Name of file to parse.
	 * @return A pair where the first item is a pointer to the fleet ArrayList and
	 *         the second one a pointer to the city object.
	 */
	public static Object[] parseInput(String filename) {
		Scanner fi = null;
		try {
			fi = new Scanner(new File(filename));
		} catch (FileNotFoundException e) {
			e.printStackTrace();
			System.exit(1);
		}
		int R = fi.nextInt();
		int C = fi.nextInt();
		int F = fi.nextInt();
		int N = fi.nextInt();
		int B = fi.nextInt();
		int T = fi.nextInt();

		ArrayList<Vehicle> fleet = new ArrayList<Vehicle>();
		ArrayList<Ride> rides = new ArrayList<Ride>();

		for (int i = 0; i < F; ++i) {
			fleet.add(new Vehicle(i));
		}

		for (int i = 0; i < N; ++i) {
			int sx = fi.nextInt();
			int sy = fi.nextInt();
			int fx = fi.nextInt();
			int fy = fi.nextInt();
			Coord start = new Coord(sx, sy);
			Coord finish = new Coord(fx, fy);
			int ts = fi.nextInt();
			int tf = fi.nextInt();
			rides.add(new Ride(i, start, finish, ts, tf));
		}

		City city = new City(R, C, B, T, rides);

		return new Object[] { fleet, city };
	}
}

class Vehicle {
	public int ID;
	public Coord pos;
	public int clock;
	public ArrayList<Ride> rides;

	public Vehicle() {
		this(-1, 0, 0);
	}

	public Vehicle(int id) {
		this(id, 0, 0);
	}

	public Vehicle(int id, int x, int y) {
		this(id, new Coord(x, y), 0);
	}

	public Vehicle(int id, Coord pos, int clock) {
		this.ID = id;
		this.pos = pos;
		this.clock = clock;
		this.rides = new ArrayList<Ride>();
	}

	/**
	 * Take a ride by adding it to this rides and updating clock and position of
	 * this Vehicle.
	 * 
	 * @param ride
	 *            Ride object representing the ride this will take.
	 */
	public void takeRide(Ride ride) {
		this.rides.add(ride);
		this.clock += this.totalTimeSpent(ride);
		this.pos = ride.finish;
	}

	/**
	 * Kills a this Vehicle by setting its clock to some value.
	 * 
	 * @param maxtime
	 *            Maximum number of steps a vehicle is allowed to make in the city.
	 */
	public void kill(int maxtime) {
		this.clock = maxtime;
	}

	@Override
	public String toString() {
		String str = "" + rides.size();
		for (Ride r : rides) {
			str += " " + r.ID;
		}
		return str;
	}

	/**
	 * Check whether this Vehicle can complete a ride and earn points from it.
	 * 
	 * @param ride
	 *            Ride to check if this Vehicle is able to complete in time.
	 * @return true if the ride can be completed in time, false otherwise.
	 */
	public boolean canComplete(Ride ride) {
		return this.clock + this.pos.distanceTo(ride.start) + ride.len <= ride.finishTime;
	}

	/**
	 * Calculate the amount of points earned by taking a ride and, eventually, the
	 * bonus. Use only to calculate points for a ride this Vehicle will take
	 * immediately.
	 * 
	 * @param ride
	 *            Ride this Vehicle is about to take.
	 * @param bonus
	 *            Amount of points to add for a ride starting on time.
	 * @return the points this Vehicle could earn by taking the given Ride
	 *         immediately.
	 */
	public double points(Ride ride, int bonus) {
		if (this.clock + this.pos.distanceTo(ride.start) > ride.startTime) {
			bonus = 0;
		}

		return ride.len + bonus;
	}

	/**
	 * Calculate the time this Vehicle will spend waiting for the earliest start of
	 * a ride.
	 * 
	 * @param ride
	 *            Ride this Vehicle is about to take.
	 * @return the time spent by this Vehicle waiting still for the ride to start.
	 */
	public int timeToWait(Ride ride) {
		return (int) (ride.startTime - this.clock - this.pos.distanceTo(ride.start));
	}

	/**
	 * Calculate the total time a ride would take.
	 * 
	 * @param ride
	 *            Ride this Vehicle is about to take.
	 * @return total time this Vehicle will invest for the given Ride.
	 */
	public int totalTimeSpent(Ride ride) {
		return this.timeWasted(ride) + ride.len;
	}

	/**
	 * Calculate the amount of time wasted by this Vehicle if a Ride is assigned.
	 * 
	 * @param ride
	 *            Ride this Vehicle is about to take.
	 * @return the time wasted by this Vehicle doing zero points.
	 */
	public int timeWasted(Ride ride) {
		int wait = this.timeToWait(ride);
		if (wait < 0) {
			wait = 0;
		}
		return this.pos.distanceTo(ride.start) + wait;
	}

	/**
	 * Calculate the score earned by this Vehicle.
	 * 
	 * @param bonus
	 *            Amount of extra points assigned for a Ride starting on time.
	 * @return the total score earned thanks to this Vehicle.
	 */
	public int totalScore(int bonus) {
		int score = 0;
		Vehicle explorer = new Vehicle();
		for (Ride ride : this.rides) {
			score += explorer.points(ride, bonus);
			explorer.takeRide(ride);
		}

		return score;
	}

	/**
	 * Find the Vehicle that free itself from the last assigned ride first.
	 * 
	 * @param cars
	 *            ArrayList of Vehicle object where such Vehicle will be searched.
	 * @return the Vehicle that free itself from the last assigned ride first.
	 */
	public static Vehicle firstFree(ArrayList<Vehicle> cars) {
		int pos_min = 0;
		for (int i = 1; i < cars.size(); ++i) {
			if (cars.get(i).clock < cars.get(pos_min).clock) {
				pos_min = i;
			}
		}

		return cars.get(pos_min);
	}
}

class Ride {
	public int ID;
	public Coord start;
	public Coord finish;
	public int startTime;
	public int finishTime;
	public int len;

	public Ride(int id, Coord start, Coord finish, int startTime, int finishTime) {
		this.ID = id;
		this.start = start;
		this.finish = finish;
		this.startTime = startTime;
		this.finishTime = finishTime;
		this.len = start.distanceTo(finish);
	}
}

class City {
	public int rows;
	public int cols;
	public int bonus;
	public int maxtime;
	public ArrayList<Ride> rides;
	public boolean[] taken;
	public char flag;

	public City(int rows, int cols, int bonus, int maxtime, ArrayList<Ride> rides) {
		this.rows = rows;
		this.cols = cols;
		this.bonus = bonus;
		this.maxtime = maxtime;
		this.rides = rides;
		this.taken = new boolean[rides.size()];
		switch (this.rows * this.cols) {
		case 3 * 4:
			this.flag = 'a';
			break;
		case 800 * 1000:
			this.flag = 'b';
			break;
		case 3000 * 2000:
			this.flag = 'c';
			break;
		case 10000 * 10000:
			this.flag = 'd';
			break;
		default:
			this.flag = 'e';
			break;
		}
	}

	/**
	 * Find the best ride to assign to a Vehicle in order to maximize the score.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRide(Vehicle vehicle) {
		switch (this.flag) {
		case 'a':
			return this.bestRideA(vehicle);
		case 'b':
			return this.bestRideB(vehicle);
		case 'c':
			return this.bestRideC(vehicle);
		case 'd':
			return this.bestRideD(vehicle);
		default:
			return this.bestRideE(vehicle);
		}

	}

	/**
	 * Test case A is very simple and we obtain 10/10 with any method.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRideA(Vehicle vehicle) {
		return this.bestRideE(vehicle);
	}

	/**
	 * In test case B the rides are uniformly distributed, so we solve this case
	 * with the base method.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRideB(Vehicle vehicle) {
		return this.bestRideE(vehicle);
	}

	/**
	 * In test case C there are 10000 rides and an they are very dense, so almost no
	 * time is wasted by moving from a finish point to a new starting point. Hence
	 * we choose the ride that maximizes the score/time ratio.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRideC(Vehicle vehicle) {
		double bestScore = -1;
		Ride bestRide = null;
		for (int i = 0; i < this.taken.length; ++i) {
			if (!this.taken[i] && vehicle.canComplete(this.rides.get(i))) {
				Ride currentRide = this.rides.get(i);
				double currentScore = vehicle.points(currentRide, this.bonus) / vehicle.totalTimeSpent(currentRide);
				if (currentScore > bestScore) {
					bestScore = currentScore;
					bestRide = currentRide;
				}
			}
		}

		return bestRide;
	}

	/**
	 * Test case D has a lot of short rides in a very small region and a few very
	 * long rides that drives the vehicles too far away to catch back up. Hence we
	 * concentrate on short rides as long as we can, and we accept very long rides
	 * only when the time is running out.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRideD(Vehicle vehicle) {
		double bestScore = -1;
		Ride bestRide = null;
		for (int i = 0; i < this.taken.length; ++i) {
			if (!this.taken[i] && vehicle.canComplete(this.rides.get(i))) {
				Ride currentRide = this.rides.get(i);
				double currentScore = vehicle.points(currentRide, this.bonus) / vehicle.totalTimeSpent(currentRide);
				if (currentRide.len > this.rows / 2) {
					if (Math.abs(vehicle.clock + vehicle.totalTimeSpent(currentRide) - currentRide.finishTime) <= 10
							&& Math.abs(vehicle.clock + vehicle.totalTimeSpent(currentRide) - this.maxtime) <= 10) {
						return currentRide;
					} else {
						currentScore = 0;
					}
				}

				if (currentScore > bestScore) {
					bestScore = currentScore;
					bestRide = currentRide;
				}
			}
		}

		return bestRide;
	}

	/**
	 * In test case E rides are uniformly distributed so the only way we rate one
	 * better than another is the actual score it makes us earn minus the time
	 * wasted by our Vehicle getting ready or waiting for such ride.
	 * 
	 * @param vehicle
	 *            Vehicle to which the Ride will be assigned.
	 * @return the optimal Ride to assign to the Vehicle.
	 */
	public Ride bestRideE(Vehicle vehicle) {
		double bestScore = Double.NEGATIVE_INFINITY;
		Ride bestRide = null;
		for (int i = 0; i < this.taken.length; ++i) {
			if (!this.taken[i] && vehicle.canComplete(this.rides.get(i))) {
				Ride currentRide = this.rides.get(i);
				double currentScore = vehicle.points(currentRide, this.bonus) - vehicle.timeWasted(currentRide);

				if (currentScore > bestScore) {
					bestScore = currentScore;
					bestRide = currentRide;
				}
			}
		}

		return bestRide;
	}

	/**
	 * Find the rides that were not assigned to any vehicle in the fleet.
	 * 
	 * @return an ArrayList of Ride objects.
	 */
	public ArrayList<Ride> remaining() {
		ArrayList<Ride> rem = new ArrayList<Ride>();
		for (int i = 0; i < this.taken.length; ++i) {
			if (!this.taken[i]) {
				rem.add(this.rides.get(i));
			}
		}

		return rem;
	}

	/**
	 * Optimize the rides of a vehicle trying to fit some of the rides that were not
	 * assigned to anyone else and eventually throwing away some of the rides that
	 * the vehicle had taken.
	 * 
	 * @param vehicle
	 *            The Vehicle to optimize.
	 * @return an optimized Vehicle whose score is the same, or greater than the
	 *         argument's one.
	 */
	public Vehicle optimize(Vehicle vehicle) {
		for (Ride ride : this.remaining()) {
			Vehicle lghost = new Vehicle();
			Vehicle hghost = new Vehicle();
			int lindex = 0;
			int hindex = 1;
			if (!lghost.canComplete(ride)) {
				continue;
			}
			hghost.takeRide(vehicle.rides.get(lindex));
			while (hindex < vehicle.rides.size() && hghost.canComplete(ride)) {
				lghost.takeRide(vehicle.rides.get(lindex++));
				hghost.takeRide(vehicle.rides.get(hindex++));
			}
			lghost.takeRide(ride);
			while (lindex < vehicle.rides.size() && lghost.canComplete(vehicle.rides.get(lindex))) {
				lghost.takeRide(vehicle.rides.get(lindex++));
			}

			if (lghost.totalScore(this.bonus) > vehicle.totalScore(this.bonus)) {
				for (Ride r : vehicle.rides) {
					this.taken[r.ID] = false;
				}
				for (Ride r : lghost.rides) {
					this.taken[r.ID] = true;
				}
				lghost.ID = vehicle.ID;
				vehicle = lghost;
			}
		}

		return vehicle;
	}
}

class Coord {
	public int x;
	public int y;

	public Coord(int x, int y) {
		this.x = x;
		this.y = y;
	}

	/**
	 * Calculate the distance from this to another Coord.
	 * 
	 * @param other
	 *            Second Coord whose distance from this has to be calculated.
	 * @return the distance calculated as |this.x - x| + |this.y - y|.
	 */
	public int distanceTo(Coord other) {
		return Math.abs(this.x - other.x) + Math.abs(this.y - other.y);
	}
}
