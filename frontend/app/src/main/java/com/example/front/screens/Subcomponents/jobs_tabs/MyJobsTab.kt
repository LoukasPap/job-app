package com.example.front.screens.Subcomponents.jobs_tabs

import android.content.Intent
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.key
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import coil.compose.AsyncImage
import com.example.front.FriendProfileActivity
import com.example.front.data.base.User
import com.example.front.data.base.UserLittleDetail
import com.example.front.data.response.JobApplied
import com.example.front.data.response.JobUploaded
import com.example.front.screens.Subcomponents.modals.JobModal

@Composable
fun MyJobsTab(appliedJobs: List<JobApplied>? = emptyList(), createdJobs: List<JobUploaded>? = emptyList(), onRevoke: (JobApplied) -> Unit) {
    val context = LocalContext.current

    var showDialog by remember { mutableStateOf(false) }
    var showApplicants by remember { mutableStateOf(false) }
    var currentAppliers by remember { mutableStateOf<List<UserLittleDetail>>(listOf()) }

    // Padding to move the header down
    Spacer(modifier = Modifier.height(20.dp))

    Column (
        horizontalAlignment = Alignment.Start,
        verticalArrangement = Arrangement.Center,
        modifier = Modifier
            .padding(start = 15.dp)
            .fillMaxSize()
            .verticalScroll(rememberScrollState())

    ) {

        // Applications Section
        Text(text = "Applications",
            fontSize = 5.em,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(start = 20.dp)
        )

        Row(
            modifier = Modifier
                .horizontalScroll(rememberScrollState())
                .fillMaxWidth(),
        ) {
            if (appliedJobs!!.isNotEmpty())
                appliedJobs.forEach { job ->
                    JobCard(job, "Revoke apply request", onApply = { onRevoke(it) }, onDismiss = {})
            } else {
                Text(text = "You haven't applied to any job yet", Modifier.padding(start = 20.dp, bottom = 15.dp))
            }
        }

        Spacer(modifier = Modifier.height(10.dp))

        // Jobs Created Section
        Text(text = "Jobs Uploaded",
            fontSize = 5.em,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(start = 20.dp)
        )

        Row(
            modifier = Modifier
                .horizontalScroll(rememberScrollState())
                .fillMaxWidth()
        ) {
            if (createdJobs!!.isNotEmpty())
                createdJobs.forEach { job ->
                    JobCard(job, button_text = "${job.applicants_list.size} Applicants", onApplyClick = {
                        currentAppliers = it
                        showApplicants = true })
            } else {
                Text(text = "You haven't uploaded any job yet", Modifier.padding(start=20.dp, bottom = 15.dp))
            }
        }

        Button(
            onClick = { showDialog = true },
            modifier = Modifier
                .clip(RoundedCornerShape(10.dp))
                .padding(horizontal = 20.dp)
                .fillMaxWidth(),
            shape = RoundedCornerShape(10.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = Color.Black,
                contentColor = Color.White
            )
        ) {

            Text("+ Upload Job")
        }
    }

    if (showApplicants) {
        ApplicantsModal(
            applicants = currentAppliers,
            onDismiss = { showApplicants = false },
        )
    }

    if (showDialog) {
        JobModal(
            onDismiss = { showDialog = false },
            onSave = { job ->
                showDialog = false
            }
        )
    }
}


@Composable
fun ApplicantsModal(
    applicants: List<UserLittleDetail>,
    onDismiss: () -> Unit,
) {
    val context = LocalContext.current
    AlertDialog(
        onDismissRequest = onDismiss,
        shape = RoundedCornerShape(5.dp),
        title = { Text(text = "Applicants") },
        modifier = Modifier.height(300.dp),
        text = {
            if (applicants.isNotEmpty()) {
                Column(modifier = Modifier.fillMaxHeight()) {
                    applicants.forEach { applicant ->
                        key(applicant) {
                            Row(
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically,
                            ) {
                                AsyncImage(
                                    model = applicant.image_url,
                                    contentScale = ContentScale.Crop,
                                    contentDescription = "profile picture",
                                    modifier = Modifier
                                        .size(30.dp)
                                        .clip(CircleShape),
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(text = applicant.user_fullname, fontSize = 4.em)
                                IconButton(onClick = {
                                    val name = applicant.user_fullname.split(" ")[0]
                                    val surname = applicant.user_fullname.split(" ")[1]
                                    val user = User(id=applicant.user_id.toString(), name=name, surname=surname, email="", imagePath = applicant.image_url)

                                    val intent = Intent(context, FriendProfileActivity::class.java)
                                    intent.putExtra("user", user)
                                    context.startActivity(intent)
                                }) {
                                    Icon(
                                        imageVector = Icons.Default.Person,
                                        contentDescription = "Back"
                                    )
                                }
                            }
                        }
                    }
                }
            } else {
                Text(
                    text = "No applicants $applicants",
                    modifier = Modifier.padding(50.dp)
                )
            }



        },
        confirmButton = {},
        dismissButton = {
            TextButton(
                onClick = onDismiss,
                shape = RoundedCornerShape(5.dp),
                colors =
                ButtonDefaults.buttonColors(
                    containerColor = Color(239, 71, 111),
                ),
            ){
                Text("Close")
            }
        }
    )
}