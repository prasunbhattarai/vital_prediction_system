import psycopg2


class Database:

    def get_connection(self):
        return psycopg2.connect(
            dbname="system_vitals",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )

    def insert_query(
        self, date, current_time, cpu_usage, cpu_freq, cpu_switches,
        memory_usage, memory_swap, disk_usage, read_write, net,
        bytes_sent, bytes_recv, battery_percent, power_plugged,
        gpu_usage, gpu_temp, top5_processes_cpu_average,
        top5_processes_cpu_std
    ):
        query = """
        INSERT INTO Vitals 
        (date, current_time_val, cpu_usage, cpu_freq, cpu_switches, memory_usage, 
        memory_swap, disk_usage, read_write, net, bytes_sent, bytes_recv, battery_percent, 
        power_plugged, gpu_usage, gpu_temp, top5_processes_cpu_average, top5_processes_cpu_std)
        VALUES 
        (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            date, current_time, cpu_usage, cpu_freq, cpu_switches,
            memory_usage, memory_swap, disk_usage, read_write, net,
            bytes_sent, bytes_recv, battery_percent, power_plugged,
            gpu_usage, gpu_temp, top5_processes_cpu_average,
            top5_processes_cpu_std
        )

        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print("INSERT ERROR:", e)
            raise
        finally:
            conn.close()

    def select_query(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Vitals")
                return cur.fetchall()
        except Exception as e:
            print("SELECT ERROR:", e)
            raise
        finally:
            conn.close()

    def select_recent(self):
        conn = self.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM Vitals ORDER BY id DESC LIMIT 1"
                )
                return cur.fetchone()
        except Exception as e:
            print("SELECT RECENT ERROR:", e)
            raise
        finally:
            conn.close()