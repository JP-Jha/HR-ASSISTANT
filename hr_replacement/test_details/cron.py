from django_cron import CronJobBase, Schedule
from test_details.models import Candidate
from django.utils import timezone
from datetime import timedelta

class CandidateDeletionCronJob(CronJobBase):
    """
    Cron job to delete candidates after 180 days (6 months) from their scheduled test time.
    """
    # To do: Time period needs to be changed accordingly:
    schedule = Schedule(run_every_mins=1)  # Run every 24 hours (1 day) 
    code = 'test_details.candidate_deletion_cron_job'  # Unique code for the cron job

    def do(self):
        print(f"Cron job running at {timezone.now()}")

        """
        Logic to delete candidates who have a scheduled test time more than 180 days ago.
        """
        now = timezone.now()  # Get the current date
        
        # Calculate the cutoff time (5 minutes ago)
        cutoff_time = now - timedelta(minutes=5)

        # # Find candidates whose test time is more than 180 days ago
        # candidates_to_delete = Candidate.objects.filter(
        #     # time_slot__lte=today - timedelta(minutes=5)
        # time_slot__lte=timezone.now() - timedelta(minutes=5)
        # )
        
        
        # Find candidates whose test time is more than 5 minutes ago
        candidates_to_delete = Candidate.objects.filter(
            time_slot__lte=cutoff_time  # Candidate's test time is older than the cutoff time
        )
        
        
        # Print for debugging purposes
        print(f"Candidates to delete: {candidates_to_delete.count()}")
        
        # Delete candidates:
        deleted_count, _ = candidates_to_delete.delete()  # Delete them from the database

        # Output the number of deleted candidates
        if deleted_count > 0:
            print(f"{deleted_count} candidates deleted successfully!")
        else:
            print("No candidates to delete.")
